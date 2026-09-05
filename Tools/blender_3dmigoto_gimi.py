#!/usr/bin/env python3

# Original plugin by DarkStarSword (https://github.com/DarkStarSword/3d-fixes/blob/master/blender_3dmigoto.py)
# Updated to support 3.0 by MicroKnightmare from the DOA modding discord

####### AGMG Discord Contributors #######

# Modified by SilentNightSound#7430 to add Genshin support and some more Genshin-specific features
# QOL feature (ignoring hidden meshes while exporting) added by HazrateGolabi#1364
# HummyR#8131

# bl_info seems to be parsed as text outside of the normal module loading by
# Blender, meaning we can't dynamically set the Blender version to indicate the
# addon supports both Blender 2.79 and 2.80. It will still work on 2.79, just
# with a warning.
bl_info = {
    "name": "3DMigoto",
    "blender": (2, 80, 0),
    "author": "Ian Munsie (darkstarsword@gmail.com), SilentNightSound#7430",
    "location": "File > Import-Export",
    "description": "Imports meshes dumped with 3DMigoto's frame analysis and exports meshes suitable for re-injection",
    "category": "Import-Export",
    "tracker_url": "https://github.com/SilentNightSound/GI-Model-Importer",
}

# TODO:
# - Option to reduce vertices on import to simplify mesh (can be noticeably lossy)
# - Option to untesselate triangles on import?
# - Operator to generate vertex group map
# - Operator to set current pose from a constant buffer dump
# - Generate bones, using vertex groups to approximate position
#   - And maybe orientation & magnitude, but I'll have to figure out some funky
#     maths to have it follow the mesh like a cylinder
# - Add support for games using multiple VBs per mesh, e.g. Witcher 3
# - Test in a wider variety of games
# - Handle TANGENT better on both import & export?

import io
import re
from array import array
import struct
import numpy
import itertools
import collections
import os
from glob import glob
import json
import copy
import textwrap
import shutil

import bpy
from bpy_extras.io_utils import unpack_list, ImportHelper, ExportHelper, axis_conversion
from bpy.props import BoolProperty, StringProperty, CollectionProperty
from bpy_extras.image_utils import load_image
from mathutils import Matrix, Vector


# In Blender 2.79 we use orientation_helper_factory / IOOBJOrientationHelper,
# while in 2.80 we use orientation_helper. We implement both APIs in code and
# provide dummy implementations for whichever is not available.
try:
    # Blender 2.80:
    from bpy_extras.io_utils import orientation_helper
    IOOBJOrientationHelper = type('DummyIOOBJOrientationHelper', (object,), {})
except ImportError:
    # Blender 2.79:
    from bpy_extras.io_utils import orientation_helper_factory
    IOOBJOrientationHelper = orientation_helper_factory("IOOBJOrientationHelper", axis_forward='-Z', axis_up='Y')
    class orientation_helper:
        def __init__(self, **orientation_kwargs):
            pass
        def __call__(self, cls):
            return cls

if bpy.app.version >= (2, 80):
    import_menu = bpy.types.TOPBAR_MT_file_import
    export_menu = bpy.types.TOPBAR_MT_file_export
    vertex_color_layer_channels = 4
else:
    import_menu = bpy.types.INFO_MT_file_import
    export_menu = bpy.types.INFO_MT_file_export
    vertex_color_layer_channels = 3

# https://theduckcow.com/2019/update-addons-both-blender-28-and-27-support/
def make_annotations(cls):
    """Converts class fields to annotations if running with Blender 2.8"""
    if bpy.app.version < (2, 80):
        return cls
    bl_props = {k: v for k, v in cls.__dict__.items() if isinstance(v, tuple)}
    if bl_props:
        if '__annotations__' not in cls.__dict__:
            setattr(cls, '__annotations__', {})
        annotations = cls.__dict__['__annotations__']
        for k, v in bl_props.items():
            annotations[k] = v
            delattr(cls, k)
    return cls

def select_get(object):
    """Multi version compatibility for getting object selection"""
    if hasattr(object, "select_get"):
        return object.select_get()
    else:
        return object.select

def select_set(object, state):
    """Multi version compatibility for setting object selection"""
    if hasattr(object, "select_set"):
        object.select_set(state)
    else:
        object.select = state

def hide_get(object):
    """Multi version compatibility for getting object hidden state"""
    if hasattr(object, "hide_get"):
        return object.hide_get()
    else:
        return object.hide

def hide_set(object, state):
    """Multi version compatibility for setting object hidden state"""
    if hasattr(object, "hide_set"):
        object.hide_set(state)
    else:
        object.hide = state

def set_active_object(context, obj):
    """Get the active object in a 2.7 and 2.8 compatible way"""
    if hasattr(context, "view_layer"):
        context.view_layer.objects.active = obj # the 2.8 way
    else:
        context.scene.objects.active = obj # the 2.7 way

def get_active_object(context):
    """Get the active object in a 2.7 and 2.8 compatible way"""
    if hasattr(context, "view_layer"):
        return context.view_layer.objects.active
    else:
        return context.scene.objects.active

def link_object_to_scene(context, obj):
    if hasattr(context.scene, "collection"): # Blender 2.80
        context.scene.collection.objects.link(obj)
    else: # Blender 2.79
        context.scene.objects.link(obj)

def unlink_object(context, obj):
    if hasattr(context.scene, "collection"): # Blender 2.80
        context.scene.collection.objects.unlink(obj)
    else: # Blender 2.79
        context.scene.objects.unlink(obj)

import operator # to get function names for operators like @, +, -
def matmul(a, b):
    """Perform matrix multiplication in a blender 2.7 and 2.8 safe way"""
    if hasattr(bpy.app, "version") and bpy.app.version >= (2, 80):
        return operator.matmul(a, b) # the same as writing a @ b
    else:
        return a * b

############## End Blender 2.7 / 2.8 compatibility wrappers ##############




def keys_to_ints(d):
    return {k.isdecimal() and int(k) or k:v for k,v in d.items()}
def keys_to_strings(d):
    return {str(k):v for k,v in d.items()}

class Fatal(Exception): pass

# TODO: Support more DXGI formats:
f32_pattern = re.compile(r'''(?:DXGI_FORMAT_)?(?:[RGBAD]32)+_FLOAT''')
f16_pattern = re.compile(r'''(?:DXGI_FORMAT_)?(?:[RGBAD]16)+_FLOAT''')
u32_pattern = re.compile(r'''(?:DXGI_FORMAT_)?(?:[RGBAD]32)+_UINT''')
u16_pattern = re.compile(r'''(?:DXGI_FORMAT_)?(?:[RGBAD]16)+_UINT''')
u8_pattern = re.compile(r'''(?:DXGI_FORMAT_)?(?:[RGBAD]8)+_UINT''')
s32_pattern = re.compile(r'''(?:DXGI_FORMAT_)?(?:[RGBAD]32)+_SINT''')
s16_pattern = re.compile(r'''(?:DXGI_FORMAT_)?(?:[RGBAD]16)+_SINT''')
s8_pattern = re.compile(r'''(?:DXGI_FORMAT_)?(?:[RGBAD]8)+_SINT''')
unorm16_pattern = re.compile(r'''(?:DXGI_FORMAT_)?(?:[RGBAD]16)+_UNORM''')
unorm8_pattern = re.compile(r'''(?:DXGI_FORMAT_)?(?:[RGBAD]8)+_UNORM''')
snorm16_pattern = re.compile(r'''(?:DXGI_FORMAT_)?(?:[RGBAD]16)+_SNORM''')
snorm8_pattern = re.compile(r'''(?:DXGI_FORMAT_)?(?:[RGBAD]8)+_SNORM''')

misc_float_pattern = re.compile(r'''(?:DXGI_FORMAT_)?(?:[RGBAD][0-9]+)+_(?:FLOAT|UNORM|SNORM)''')
misc_int_pattern = re.compile(r'''(?:DXGI_FORMAT_)?(?:[RGBAD][0-9]+)+_[SU]INT''')

def EncoderDecoder(fmt):
    if f32_pattern.match(fmt):
        return (lambda data: b''.join(struct.pack('<f', x) for x in data),
                lambda data: numpy.frombuffer(data, numpy.float32).tolist())
    if f16_pattern.match(fmt):
        return (lambda data: numpy.fromiter(data, numpy.float16).tobytes(),
                lambda data: numpy.frombuffer(data, numpy.float16).tolist())
    if u32_pattern.match(fmt):
        return (lambda data: numpy.fromiter(data, numpy.uint32).tobytes(),
                lambda data: numpy.frombuffer(data, numpy.uint32).tolist())
    if u16_pattern.match(fmt):
        return (lambda data: numpy.fromiter(data, numpy.uint16).tobytes(),
                lambda data: numpy.frombuffer(data, numpy.uint16).tolist())
    if u8_pattern.match(fmt):
        return (lambda data: numpy.fromiter(data, numpy.uint8).tobytes(),
                lambda data: numpy.frombuffer(data, numpy.uint8).tolist())
    if s32_pattern.match(fmt):
        return (lambda data: numpy.fromiter(data, numpy.int32).tobytes(),
                lambda data: numpy.frombuffer(data, numpy.int32).tolist())
    if s16_pattern.match(fmt):
        return (lambda data: numpy.fromiter(data, numpy.int16).tobytes(),
                lambda data: numpy.frombuffer(data, numpy.int16).tolist())
    if s8_pattern.match(fmt):
        return (lambda data: numpy.fromiter(data, numpy.int8).tobytes(),
                lambda data: numpy.frombuffer(data, numpy.int8).tolist())

    if unorm16_pattern.match(fmt):
        return (lambda data: numpy.around((numpy.fromiter(data, numpy.float32) * 65535.0)).astype(numpy.uint16).tobytes(),
                lambda data: (numpy.frombuffer(data, numpy.uint16) / 65535.0).tolist())
    if unorm8_pattern.match(fmt):
        return (lambda data: numpy.around((numpy.fromiter(data, numpy.float32) * 255.0)).astype(numpy.uint8).tobytes(),
                lambda data: (numpy.frombuffer(data, numpy.uint8) / 255.0).tolist())
    if snorm16_pattern.match(fmt):
        return (lambda data: numpy.around((numpy.fromiter(data, numpy.float32) * 32767.0)).astype(numpy.int16).tobytes(),
                lambda data: (numpy.frombuffer(data, numpy.int16) / 32767.0).tolist())
    if snorm8_pattern.match(fmt):
        return (lambda data: numpy.around((numpy.fromiter(data, numpy.float32) * 127.0)).astype(numpy.int8).tobytes(),
                lambda data: (numpy.frombuffer(data, numpy.int8) / 127.0).tolist())

    raise Fatal('File uses an unsupported DXGI Format: %s' % fmt)

components_pattern = re.compile(r'''(?<![0-9])[0-9]+(?![0-9])''')
def format_components(fmt):
    return len(components_pattern.findall(fmt))

def format_size(fmt):
    matches = components_pattern.findall(fmt)
    return sum(map(int, matches)) // 8

class InputLayoutElement(object):
    def __init__(self, arg):
        if isinstance(arg, io.IOBase):
            self.from_file(arg)
        else:
            self.from_dict(arg)

        self.encoder, self.decoder = EncoderDecoder(self.Format)

    def from_file(self, f):
        self.SemanticName = self.next_validate(f, 'SemanticName')
        self.SemanticIndex = int(self.next_validate(f, 'SemanticIndex'))
        self.Format = self.next_validate(f, 'Format')
        self.InputSlot = int(self.next_validate(f, 'InputSlot'))
        self.AlignedByteOffset = self.next_validate(f, 'AlignedByteOffset')
        if self.AlignedByteOffset == 'append':
            raise Fatal('Input layouts using "AlignedByteOffset=append" are not yet supported')
        self.AlignedByteOffset = int(self.AlignedByteOffset)
        self.InputSlotClass = self.next_validate(f, 'InputSlotClass')
        self.InstanceDataStepRate = int(self.next_validate(f, 'InstanceDataStepRate'))

    def to_dict(self):
        d = {}
        d['SemanticName'] = self.SemanticName
        d['SemanticIndex'] = self.SemanticIndex
        d['Format'] = self.Format
        d['InputSlot'] = self.InputSlot
        d['AlignedByteOffset'] = self.AlignedByteOffset
        d['InputSlotClass'] = self.InputSlotClass
        d['InstanceDataStepRate'] = self.InstanceDataStepRate
        return d

    def to_string(self, indent=2):
        return textwrap.indent(textwrap.dedent('''
            SemanticName: %s
            SemanticIndex: %i
            Format: %s
            InputSlot: %i
            AlignedByteOffset: %i
            InputSlotClass: %s
            InstanceDataStepRate: %i
        ''').lstrip() % (
            self.SemanticName,
            self.SemanticIndex,
            self.Format,
            self.InputSlot,
            self.AlignedByteOffset,
            self.InputSlotClass,
            self.InstanceDataStepRate,
        ), ' '*indent)

    def from_dict(self, d):
        self.SemanticName = d['SemanticName']
        self.SemanticIndex = d['SemanticIndex']
        self.Format = d['Format']
        self.InputSlot = d['InputSlot']
        self.AlignedByteOffset = d['AlignedByteOffset']
        self.InputSlotClass = d['InputSlotClass']
        self.InstanceDataStepRate = d['InstanceDataStepRate']

    @staticmethod
    def next_validate(f, field):
        line = next(f).strip()
        assert(line.startswith(field + ': '))
        return line[len(field) + 2:]

    @property
    def name(self):
        if self.SemanticIndex:
            return '%s%i' % (self.SemanticName, self.SemanticIndex)
        return self.SemanticName

    def pad(self, data, val):
        padding = format_components(self.Format) - len(data)
        assert(padding >= 0)
        return data + [val]*padding

    def clip(self, data):
        return data[:format_components(self.Format)]

    def size(self):
        return format_size(self.Format)

    def is_float(self):
        return misc_float_pattern.match(self.Format)

    def is_int(self):
        return misc_int_pattern.match(self.Format)

    def encode(self, data):
        # print(self.Format, data)
        return self.encoder(data)

    def decode(self, data):
        return self.decoder(data)

    def __eq__(self, other):
        return \
            self.SemanticName == other.SemanticName and \
            self.SemanticIndex == other.SemanticIndex and \
            self.Format == other.Format and \
            self.InputSlot == other.InputSlot and \
            self.AlignedByteOffset == other.AlignedByteOffset and \
            self.InputSlotClass == other.InputSlotClass and \
            self.InstanceDataStepRate == other.InstanceDataStepRate

class InputLayout(object):
    def __init__(self, custom_prop=[], stride=0):
        self.elems = collections.OrderedDict()
        self.stride = stride
        for item in custom_prop:
            elem = InputLayoutElement(item)
            self.elems[elem.name] = elem

    def serialise(self):
        return [x.to_dict() for x in self.elems.values()]

    def to_string(self):
        ret = ''
        for i, elem in enumerate(self.elems.values()):
            ret += 'element[%i]:\n' % i
            ret += elem.to_string()
        return ret

    def parse_element(self, f):
        elem = InputLayoutElement(f)
        self.elems[elem.name] = elem

    def __iter__(self):
        return iter(self.elems.values())

    def __getitem__(self, semantic):
        return self.elems[semantic]

    def encode(self, vertex):
        buf = bytearray(self.stride)

        for semantic, data in vertex.items():
            if semantic.startswith('~'):
                continue
            elem = self.elems[semantic]
            data = elem.encode(data)
            buf[elem.AlignedByteOffset:elem.AlignedByteOffset + len(data)] = data

        assert(len(buf) == self.stride)
        return buf

    def decode(self, buf):
        vertex = {}
        for elem in self.elems.values():
            data = buf[elem.AlignedByteOffset:elem.AlignedByteOffset + elem.size()]
            vertex[elem.name] = elem.decode(data)
        return vertex

    def __eq__(self, other):
        return self.elems == other.elems

class HashableVertex(dict):
    def __hash__(self):
        # Convert keys and values into immutable types that can be hashed
        immutable = tuple((k, tuple(v)) for k,v in sorted(self.items()))
        return hash(immutable)

class VertexBuffer(object):
    vb_elem_pattern = re.compile(r'''vb\d+\[\d*\]\+\d+ (?P<semantic>[^:]+): (?P<data>.*)$''')

    # Python gotcha - do not set layout=InputLayout() in the default function
    # parameters, as they would all share the *same* InputLayout since the
    # default values are only evaluated once on file load
    def __init__(self, f=None, layout=None, load_vertices=True):
        self.vertices = []
        self.layout = layout and layout or InputLayout()
        self.first = 0
        self.vertex_count = 0
        self.offset = 0
        self.topology = 'trianglelist'

        if f is not None:
            self.parse_vb_txt(f, load_vertices)

    def parse_vb_txt(self, f, load_vertices):
        for line in map(str.strip, f):
            # print(line)
            if line.startswith('byte offset:'):
                self.offset = int(line[13:])
            if line.startswith('first vertex:'):
                self.first = int(line[14:])
            if line.startswith('vertex count:'):
                self.vertex_count = int(line[14:])
            if line.startswith('stride:'):
                self.layout.stride = int(line[7:])
            if line.startswith('element['):
                self.layout.parse_element(f)
            if line.startswith('topology:'):
                self.topology = line[10:]
                if line != 'topology: trianglelist':
                    raise Fatal('"%s" is not yet supported' % line)
            if line.startswith('vertex-data:'):
                if not load_vertices:
                    return
                self.parse_vertex_data(f)
        assert(len(self.vertices) == self.vertex_count)

    def parse_vb_bin(self, f):
        f.seek(self.offset)
        # XXX: Should we respect the first/base vertex?
        # f.seek(self.first * self.layout.stride, whence=1)
        self.first = 0
        while True:
            vertex = f.read(self.layout.stride)
            if not vertex:
                break
            self.vertices.append(self.layout.decode(vertex))
        # We intentionally disregard the vertex count when loading from a
        # binary file, as we assume frame analysis might have only dumped a
        # partial buffer to the .txt files (e.g. if this was from a dump where
        # the draw call index count was overridden it may be cut short, or
        # where the .txt files contain only sub-meshes from each draw call and
        # we are loading the .buf file because it contains the entire mesh):
        self.vertex_count = len(self.vertices)

    def append(self, vertex):
        self.vertices.append(vertex)
        self.vertex_count += 1

    def parse_vertex_data(self, f):
        vertex = {}
        for line in map(str.strip, f):
            #print(line)
            if line.startswith('instance-data:'):
                break

            match = self.vb_elem_pattern.match(line)
            if match:
                vertex[match.group('semantic')] = self.parse_vertex_element(match)
            elif line == '' and vertex:
                self.vertices.append(vertex)
                vertex = {}
        if vertex:
            self.vertices.append(vertex)

    def parse_vertex_element(self, match):
        fields = match.group('data').split(',')

        if self.layout[match.group('semantic')].Format.endswith('INT'):
            return tuple(map(int, fields))

        return tuple(map(float, fields))

    def remap_blendindices(self, obj, mapping):
        def lookup_vgmap(x):
            vgname = obj.vertex_groups[x].name
            return mapping.get(vgname, mapping.get(x, x))

        for vertex in self.vertices:
            for semantic in list(vertex):
                if semantic.startswith('BLENDINDICES'):
                    vertex['~' + semantic] = vertex[semantic]
                    vertex[semantic] = tuple(lookup_vgmap(x) for x in vertex[semantic])

    def revert_blendindices_remap(self):
        # Significantly faster than doing a deep copy
        for vertex in self.vertices:
            for semantic in list(vertex):
                if semantic.startswith('BLENDINDICES'):
                    vertex[semantic] = vertex['~' + semantic]
                    del vertex['~' + semantic]

    def disable_blendweights(self):
        for vertex in self.vertices:
            for semantic in list(vertex):
                if semantic.startswith('BLENDINDICES'):
                    vertex[semantic] = (0, 0, 0, 0)

    def write(self, output, operator=None):
        for vertex in self.vertices:
            output.write(self.layout.encode(vertex))

        msg = 'Wrote %i vertices to %s' % (len(self), output.name)
        if operator:
            operator.report({'INFO'}, msg)
        else:
            print(msg)

    def __len__(self):
        return len(self.vertices)

    def merge(self, other):
        if self.layout != other.layout:
            raise Fatal('Vertex buffers have different input layouts - ensure you are only trying to merge the same vertex buffer split across multiple draw calls')
        if self.first != other.first:
            # FIXME: Future 3DMigoto might automatically set first from the
            # index buffer and chop off unreferenced vertices to save space
            raise Fatal('Cannot merge multiple vertex buffers - please check for updates of the 3DMigoto import script, or import each buffer separately')
        self.vertices.extend(other.vertices[self.vertex_count:])
        self.vertex_count = max(self.vertex_count, other.vertex_count)
        assert(len(self.vertices) == self.vertex_count)

    def wipe_semantic_for_testing(self, semantic, val=0):
        print('WARNING: WIPING %s FOR TESTING PURPOSES!!!' % semantic)
        semantic, _, components = semantic.partition('.')
        if components:
            components = [{'x':0, 'y':1, 'z':2, 'w':3}[c] for c in components]
        else:
            components = range(4)
        for vertex in self.vertices:
            for s in list(vertex):
                if s == semantic:
                    v = list(vertex[semantic])
                    for component in components:
                        if component < len(v):
                            v[component] = val
                    vertex[semantic] = v

class IndexBuffer(object):
    def __init__(self, *args, load_indices=True):
        self.faces = []
        self.first = 0
        self.index_count = 0
        self.format = 'DXGI_FORMAT_UNKNOWN'
        self.offset = 0
        self.topology = 'trianglelist'

        if isinstance(args[0], io.IOBase):
            assert(len(args) == 1)
            self.parse_ib_txt(args[0], load_indices)
        else:
            self.format, = args

        self.encoder, self.decoder = EncoderDecoder(self.format)

    def append(self, face):
        self.faces.append(face)
        self.index_count += len(face)

    def parse_ib_txt(self, f, load_indices):
        for line in map(str.strip, f):
            if line.startswith('byte offset:'):
                self.offset = int(line[13:])
            if line.startswith('first index:'):
                self.first = int(line[13:])
            elif line.startswith('index count:'):
                self.index_count = int(line[13:])
            elif line.startswith('topology:'):
                self.topology = line[10:]
                if line != 'topology: trianglelist':
                    raise Fatal('"%s" is not yet supported' % line)
            elif line.startswith('format:'):
                self.format = line[8:]
            elif line == '':
                if not load_indices:
                    return
                self.parse_index_data(f)
        assert(len(self.faces) * 3 == self.index_count)

    def parse_ib_bin(self, f):
        f.seek(self.offset)
        stride = format_size(self.format)
        # XXX: Should we respect the first index?
        # f.seek(self.first * stride, whence=1)
        self.first = 0

        face = []
        while True:
            index = f.read(stride)
            if not index:
                break
            face.append(*self.decoder(index))
            if len(face) == 3:
                self.faces.append(tuple(face))
                face = []
        assert(len(face) == 0)

        # We intentionally disregard the index count when loading from a
        # binary file, as we assume frame analysis might have only dumped a
        # partial buffer to the .txt files (e.g. if this was from a dump where
        # the draw call index count was overridden it may be cut short, or
        # where the .txt files contain only sub-meshes from each draw call and
        # we are loading the .buf file because it contains the entire mesh):
        self.index_count = len(self.faces) * 3

    def parse_index_data(self, f):
        for line in map(str.strip, f):
            face = tuple(map(int, line.split()))
            assert(len(face) == 3)
            self.faces.append(face)

    def merge(self, other):
        if self.format != other.format:
            raise Fatal('Index buffers have different formats - ensure you are only trying to merge the same index buffer split across multiple draw calls')
        self.first = min(self.first, other.first)
        self.index_count += other.index_count
        self.faces.extend(other.faces)

    def write(self, output, operator=None):
        for face in self.faces:
            output.write(self.encoder(face))

        msg = 'Wrote %i indices to %s' % (len(self), output.name)
        if operator:
            operator.report({'INFO'}, msg)
        else:
            print(msg)

    def __len__(self):
        return len(self.faces) * 3

def load_3dmigoto_mesh_bin(operator, vb_paths, ib_paths, pose_path):
    if len(vb_paths) != 1 or len(ib_paths) > 1:
        raise Fatal('Cannot merge meshes loaded from binary files')

    # Loading from binary files, but still need to use the .txt files as a
    # reference for the format:
    vb_bin_path, vb_txt_path = vb_paths[0]
    ib_bin_path, ib_txt_path = ib_paths[0]

    vb = VertexBuffer(open(vb_txt_path, 'r'), load_vertices=False)
    vb.parse_vb_bin(open(vb_bin_path, 'rb'))

    ib = None
    if ib_paths:
        ib = IndexBuffer(open(ib_txt_path, 'r'), load_indices=False)
        ib.parse_ib_bin(open(ib_bin_path, 'rb'))

    return vb, ib, os.path.basename(vb_bin_path), pose_path

def load_3dmigoto_mesh(operator, paths):
    vb_paths, ib_paths, use_bin, pose_path = zip(*paths)
    pose_path = pose_path[0]

    if use_bin[0]:
        return load_3dmigoto_mesh_bin(operator, vb_paths, ib_paths, pose_path)

    vb = VertexBuffer(open(vb_paths[0], 'r'))
    # Merge additional vertex buffers for meshes split over multiple draw calls:
    for vb_path in vb_paths[1:]:
        tmp = VertexBuffer(open(vb_path, 'r'))
        vb.merge(tmp)

    # For quickly testing how importent any unsupported semantics may be:
    #vb.wipe_semantic_for_testing('POSITION.w', 1.0)
    #vb.wipe_semantic_for_testing('TEXCOORD.w', 0.0)
    #vb.wipe_semantic_for_testing('TEXCOORD5', 0)
    #vb.wipe_semantic_for_testing('BINORMAL')
    #vb.wipe_semantic_for_testing('TANGENT')
    #vb.write(open(os.path.join(os.path.dirname(vb_paths[0]), 'TEST.vb'), 'wb'), operator=operator)

    ib = None
    if ib_paths:
        ib = IndexBuffer(open(ib_paths[0], 'r'))
        # Merge additional vertex buffers for meshes split over multiple draw calls:
        for ib_path in ib_paths[1:]:
            tmp = IndexBuffer(open(ib_path, 'r'))
            ib.merge(tmp)

    return vb, ib, os.path.basename(vb_paths[0]), pose_path

def import_normals_step1(mesh, data):
    # Ensure normals are 3-dimensional:
    # XXX: Assertion triggers in DOA6
    if len(data[0]) == 4:
        if [x[3] for x in data] != [0.0]*len(data):
            raise Fatal('Normals are 4D')
    normals = [(x[0], x[1], x[2]) for x in data]

    # To make sure the normals don't get lost by Blender's edit mode,
    # or mesh.update() we need to set custom normals in the loops, not
    # vertices.
    #
    # For testing, to make sure our normals are preserved let's use
    # garbage ones:
    #import random
    #normals = [(random.random() * 2 - 1,random.random() * 2 - 1,random.random() * 2 - 1) for x in normals]
    #
    # Comment from other import scripts:
    # Note: we store 'temp' normals in loops, since validate() may alter final mesh,
    #       we can only set custom lnors *after* calling it.
    mesh.create_normals_split()
    for l in mesh.loops:
        l.normal[:] = normals[l.vertex_index]

def import_normals_step2(mesh):
    # Taken from import_obj/import_fbx
    clnors = array('f', [0.0] * (len(mesh.loops) * 3))
    mesh.loops.foreach_get("normal", clnors)

    # Not sure this is still required with use_auto_smooth, but the other
    # importers do it, and at the very least it shouldn't hurt...
    mesh.polygons.foreach_set("use_smooth", [True] * len(mesh.polygons))

    mesh.normals_split_custom_set(tuple(zip(*(iter(clnors),) * 3)))
    mesh.use_auto_smooth = True # This has a double meaning, one of which is to use the custom normals
    # XXX CHECKME: show_edge_sharp moved in 2.80, but I can't actually
    # recall what it does and have a feeling it was unimportant:
    #mesh.show_edge_sharp = True

def import_vertex_groups(mesh, obj, blend_indices, blend_weights):
    assert(len(blend_indices) == len(blend_weights))
    if blend_indices:
        # We will need to make sure we re-export the same blend indices later -
        # that they haven't been renumbered. Not positive whether it is better
        # to use the vertex group index, vertex group name or attach some extra
        # data. Make sure the indices and names match:
        num_vertex_groups = max(itertools.chain(*itertools.chain(*blend_indices.values()))) + 1
        for i in range(num_vertex_groups):
            obj.vertex_groups.new(name=str(i))
        for vertex in mesh.vertices:
            for semantic_index in sorted(blend_indices.keys()):
                for i, w in zip(blend_indices[semantic_index][vertex.index], blend_weights[semantic_index][vertex.index]):
                    if w == 0.0:
                        continue
                    obj.vertex_groups[i].add((vertex.index,), w, 'REPLACE')
def import_uv_layers(mesh, obj, texcoords, flip_texcoord_v):
    for (texcoord, data) in sorted(texcoords.items()):
        # TEXCOORDS can have up to four components, but UVs can only have two
        # dimensions. Not positive of the best way to handle this in general,
        # but for now I'm thinking that splitting the TEXCOORD into two sets of
        # UV coordinates might work:
        dim = len(data[0])
        if dim == 4:
            components_list = ('xy', 'zw')
        elif dim == 2:
            components_list = ('xy',)
        else:
            raise Fatal('Unhandled TEXCOORD dimension: %i' % dim)
        cmap = {'x': 0, 'y': 1, 'z': 2, 'w': 3}

        for components in components_list:
            uv_name = 'TEXCOORD%s.%s' % (texcoord and texcoord or '', components)
            if hasattr(mesh, 'uv_textures'): # 2.79
                mesh.uv_textures.new(uv_name)
            else: # 2.80
                mesh.uv_layers.new(name=uv_name)
            blender_uvs = mesh.uv_layers[uv_name]

            # This will assign a texture to the UV layer, which works fine but
            # working out which texture maps to which UV layer is guesswork
            # before the import and the artist may as well just assign it
            # themselves in the UV editor pane when they can see the unwrapped
            # mesh to compare it with the dumped textures:
            #
            #path = textures.get(uv_layer, None)
            #if path is not None:
            #    image = load_image(path)
            #    for i in range(len(mesh.polygons)):
            #        mesh.uv_textures[uv_layer].data[i].image = image

            # Can't find an easy way to flip the display of V in Blender, so
            # add an option to flip it on import & export:
            if flip_texcoord_v:
                flip_uv = lambda uv: (uv[0], 1.0 - uv[1])
                # Record that V was flipped so we know to undo it when exporting:
                obj['3DMigoto:' + uv_name] = {'flip_v': True}
            else:
                flip_uv = lambda uv: uv

            uvs = [[d[cmap[c]] for c in components] for d in data]
            for l in mesh.loops:
                blender_uvs.data[l.index].uv = flip_uv(uvs[l.vertex_index])

# This loads unknown data from the vertex buffers as vertex layers
def import_vertex_layers(mesh, obj, vertex_layers):
    for (element_name, data) in sorted(vertex_layers.items()):
        dim = len(data[0])
        cmap = {0: 'x', 1: 'y', 2: 'z', 3: 'w'}
        for component in range(dim):

            if dim != 1 or element_name.find('.') == -1:
                layer_name = '%s.%s' % (element_name, cmap[component])
            else:
                layer_name = element_name

            if type(data[0][0]) == int:
                mesh.vertex_layers_int.new(name=layer_name)
                layer = mesh.vertex_layers_int[layer_name]
                for v in mesh.vertices:
                    val = data[v.index][component]
                    # Blender integer layers are 32bit signed and will throw an
                    # exception if we are assigning an unsigned value that
                    # can't fit in that range. Reinterpret as signed if necessary:
                    if val < 0x80000000:
                        layer.data[v.index].value = val
                    else:
                        layer.data[v.index].value = struct.unpack('i', struct.pack('I', val))[0]
            elif type(data[0][0]) == float:
                mesh.vertex_layers_float.new(name=layer_name)
                layer = mesh.vertex_layers_float[layer_name]
                for v in mesh.vertices:
                    layer.data[v.index].value = data[v.index][component]
            else:
                raise Fatal('BUG: Bad layer type %s' % type(data[0][0]))

def import_faces_from_ib(mesh, ib):
    mesh.loops.add(len(ib.faces) * 3)
    mesh.polygons.add(len(ib.faces))
    mesh.loops.foreach_set('vertex_index', unpack_list(ib.faces))
    mesh.polygons.foreach_set('loop_start', [x*3 for x in range(len(ib.faces))])
    mesh.polygons.foreach_set('loop_total', [3] * len(ib.faces))

def import_faces_from_vb(mesh, vb):
    # Only lightly tested
    num_faces = len(vb.vertices) // 3
    mesh.loops.add(num_faces * 3)
    mesh.polygons.add(num_faces)
    mesh.loops.foreach_set('vertex_index', [x for x in range(num_faces * 3)])
    mesh.polygons.foreach_set('loop_start', [x*3 for x in range(num_faces)])
    mesh.polygons.foreach_set('loop_total', [3] * num_faces)

def import_vertices(mesh, vb):
    mesh.vertices.add(len(vb.vertices))

    seen_offsets = set()
    blend_indices = {}
    blend_weights = {}
    texcoords = {}
    vertex_layers = {}
    use_normals = False

    for elem in vb.layout:
        if elem.InputSlotClass != 'per-vertex':
            continue

        # TODO: Allow poorly named semantics to map to other meanings to be
        # properly interpreted. This still needs to be added to the GUI, and
        # mapped back on export. Alternatively, you can alter the input
        # assembler layout format in the vb*.txt / *.fmt files prior to import.
        semantic_translations = {
            #'ATTRIBUTE': 'POSITION', # UE4
        }
        translated_elem_name = semantic_translations.get(elem.name, elem.name)

        # Discard elements that reuse offsets in the vertex buffer, e.g. COLOR
        # and some TEXCOORDs may be aliases of POSITION:
        if (elem.InputSlot, elem.AlignedByteOffset) in seen_offsets:
            assert(translated_elem_name != 'POSITION')
            continue
        seen_offsets.add((elem.InputSlot, elem.AlignedByteOffset))

        data = tuple( x[elem.name] for x in vb.vertices )
        if translated_elem_name == 'POSITION':
            # Ensure positions are 3-dimensional:
            if len(data[0]) == 4:
                if ([x[3] for x in data] != [1.0]*len(data)):
                    # XXX: Leaving this fatal error in for now, as the meshes
                    # it triggers on in DOA6 (skirts) lie about almost every
                    # semantic and we cannot import them with this version of
                    # the script regardless. Comment it out if you want to try
                    # importing anyway and preserving the W coordinate in a
                    # vertex group. It might also be possible to project this
                    # back into 3D if we assume the coordinates are homogeneous
                    # (i.e. divide XYZ by W), but that might be assuming too
                    # much for a generic script.
                    raise Fatal('Positions are 4D')
                    # Occurs in some meshes in DOA6, such as skirts.
                    # W coordinate must be preserved in these cases.
                    print('Positions are 4D, storing W coordinate in POSITION.w vertex layer')
                    vertex_layers['POSITION.w'] = [[x[3]] for x in data]
            positions = [(x[0], x[1], x[2]) for x in data]
            mesh.vertices.foreach_set('co', unpack_list(positions))
        elif translated_elem_name.startswith('COLOR'):
            if len(data[0]) <= 3 or vertex_color_layer_channels == 4:
                # Either a monochrome/RGB layer, or Blender 2.80 which uses 4
                # channel layers
                mesh.vertex_colors.new(name=elem.name)
                color_layer = mesh.vertex_colors[elem.name].data
                c = vertex_color_layer_channels
                for l in mesh.loops:
                    color_layer[l.index].color = list(data[l.vertex_index]) + [0]*(c-len(data[l.vertex_index]))
            else:
                mesh.vertex_colors.new(name=elem.name + '.RGB')
                mesh.vertex_colors.new(name=elem.name + '.A')
                color_layer = mesh.vertex_colors[elem.name + '.RGB'].data
                alpha_layer = mesh.vertex_colors[elem.name + '.A'].data
                for l in mesh.loops:
                    color_layer[l.index].color = data[l.vertex_index][:3]
                    alpha_layer[l.index].color = [data[l.vertex_index][3], 0, 0]
        elif translated_elem_name == 'NORMAL':
            use_normals = True
            import_normals_step1(mesh, data)
        elif translated_elem_name in ('TANGENT', 'BINORMAL'):
        #    # XXX: loops.tangent is read only. Not positive how to handle
        #    # this, or if we should just calculate it when re-exporting.
        #    for l in mesh.loops:
        #        assert(data[l.vertex_index][3] in (1.0, -1.0))
        #        l.tangent[:] = data[l.vertex_index][0:3]
            print('NOTICE: Skipping import of %s in favour of recalculating on export' % elem.name)
        elif translated_elem_name.startswith('BLENDINDICES'):
            blend_indices[elem.SemanticIndex] = data
        elif translated_elem_name.startswith('BLENDWEIGHT'):
            blend_weights[elem.SemanticIndex] = data
        elif translated_elem_name.startswith('TEXCOORD') and elem.is_float():
            texcoords[elem.SemanticIndex] = data
        else:
            print('NOTICE: Storing unhandled semantic %s %s as vertex layer' % (elem.name, elem.Format))
            vertex_layers[elem.name] = data

    return (blend_indices, blend_weights, texcoords, vertex_layers, use_normals)

def import_3dmigoto(operator, context, paths, merge_meshes=True, **kwargs):
    if merge_meshes:
        return import_3dmigoto_vb_ib(operator, context, paths, **kwargs)
    else:
        obj = []
        for p in paths:
            try:
                obj.append(import_3dmigoto_vb_ib(operator, context, [p], **kwargs))
            except Fatal as e:
                operator.report({'ERROR'}, str(e) + ': ' + str(p[:2]))
        # FIXME: Group objects together
        return obj

def import_3dmigoto_vb_ib(operator, context, paths, flip_texcoord_v=True, axis_forward='-Z', axis_up='Y', pose_cb_off=[0,0], pose_cb_step=1):
    vb, ib, name, pose_path = load_3dmigoto_mesh(operator, paths)

    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(mesh.name, mesh)

    global_matrix = axis_conversion(from_forward=axis_forward, from_up=axis_up).to_4x4()
    obj.matrix_world = global_matrix

    # Attach the vertex buffer layout to the object for later exporting. Can't
    # seem to retrieve this if attached to the mesh - to_mesh() doesn't copy it:
    obj['3DMigoto:VBLayout'] = vb.layout.serialise()
    obj['3DMigoto:VBStride'] = vb.layout.stride # FIXME: Strides of multiple vertex buffers
    obj['3DMigoto:FirstVertex'] = vb.first

    if ib is not None:
        import_faces_from_ib(mesh, ib)
        # Attach the index buffer layout to the object for later exporting.
        if ib.format == "DXGI_FORMAT_R16_UINT":
            obj['3DMigoto:IBFormat'] = "DXGI_FORMAT_R32_UINT"
        else:
            obj['3DMigoto:IBFormat'] = ib.format
        obj['3DMigoto:FirstIndex'] = ib.first
    else:
        import_faces_from_vb(mesh, vb)

    (blend_indices, blend_weights, texcoords, vertex_layers, use_normals) = import_vertices(mesh, vb)

    import_uv_layers(mesh, obj, texcoords, flip_texcoord_v)

    import_vertex_layers(mesh, obj, vertex_layers)

    import_vertex_groups(mesh, obj, blend_indices, blend_weights)

    # Validate closes the loops so they don't disappear after edit mode and probably other important things:
    mesh.validate(verbose=False, clean_customdata=False)  # *Very* important to not remove lnors here!
    # Not actually sure update is necessary. It seems to update the vertex normals, not sure what else:
    mesh.update()

    # Must be done after validate step:
    if use_normals:
        import_normals_step2(mesh)
    else:
        mesh.calc_normals()

    link_object_to_scene(context, obj)
    select_set(obj, True)
    set_active_object(context, obj)

    if pose_path is not None:
        import_pose(operator, context, pose_path, limit_bones_to_vertex_groups=True,
                axis_forward=axis_forward, axis_up=axis_up,
                pose_cb_off=pose_cb_off, pose_cb_step=pose_cb_step)
        set_active_object(context, obj)

    return obj

# from export_obj:
def mesh_triangulate(me):
    import bmesh
    bm = bmesh.new()
    bm.from_mesh(me)
    bmesh.ops.triangulate(bm, faces=bm.faces)
    bm.to_mesh(me)
    bm.free()

def blender_vertex_to_3dmigoto_vertex(mesh, obj, blender_loop_vertex, layout, texcoords):
    blender_vertex = mesh.vertices[blender_loop_vertex.vertex_index]
    pos = list(blender_vertex.undeformed_co)
    vertex = {}
    seen_offsets = set()

    # TODO: Warn if vertex is in too many vertex groups for this layout,
    # ignoring groups with weight=0.0
    vertex_groups = sorted(blender_vertex.groups, key=lambda x: x.weight, reverse=True)

    for elem in layout:
        if elem.InputSlotClass != 'per-vertex':
            continue

        if (elem.InputSlot, elem.AlignedByteOffset) in seen_offsets:
            continue
        seen_offsets.add((elem.InputSlot, elem.AlignedByteOffset))

        if elem.name == 'POSITION':
            if 'POSITION.w' in mesh.vertex_layers_float:
                vertex[elem.name] = pos + [mesh.vertex_layers_float['POSITION.w'].data[blender_loop_vertex.vertex_index].value]
            else:
                vertex[elem.name] = elem.pad(pos, 1.0)
        elif elem.name.startswith('COLOR'):
            if elem.name in mesh.vertex_colors:
                vertex[elem.name] = elem.clip(list(mesh.vertex_colors[elem.name].data[blender_loop_vertex.index].color))
            else:
                try:
                    vertex[elem.name] = list(mesh.vertex_colors[elem.name+'.RGB'].data[blender_loop_vertex.index].color)[:3] + \
                                            [mesh.vertex_colors[elem.name+'.A'].data[blender_loop_vertex.index].color[0]]
                except KeyError:
                    raise Fatal("ERROR: Unable to find COLOR property. Ensure the model you are exporting has a color attribute (of type Face Corner/Byte Color) called COLOR")
        elif elem.name == 'NORMAL':
            vertex[elem.name] = elem.pad(list(blender_loop_vertex.normal), 0.0)
        elif elem.name.startswith('TANGENT'):
            # DOAXVV has +1/-1 in the 4th component. Not positive what this is,
            # but guessing maybe the bitangent sign? Not even sure it is used...
            # FIXME: Other games
                #temporarily set tangent to normal for Anime Game since blender doesnt wanna import tangent
            vertex[elem.name] = elem.pad(list(blender_loop_vertex.normal), blender_loop_vertex.bitangent_sign)
        elif elem.name.startswith('BINORMAL'):
            # Some DOA6 meshes (skirts) use BINORMAL, but I'm not certain it is
            # actually the binormal. These meshes are weird though, since they
            # use 4 dimensional positions and normals, so they aren't something
            # we can really deal with at all. Therefore, the below is untested,
            # FIXME: So find a mesh where this is actually the binormal,
            # uncomment the below code and test.
            # normal = blender_loop_vertex.normal
            # tangent = blender_loop_vertex.tangent
            # binormal = numpy.cross(normal, tangent)
            # XXX: Does the binormal need to be normalised to a unit vector?
            # binormal = binormal / numpy.linalg.norm(binormal)
            # vertex[elem.name] = elem.pad(list(binormal), 0.0)
            pass
        elif elem.name.startswith('BLENDINDICES'):
            i = elem.SemanticIndex * 4
            vertex[elem.name] = elem.pad([ x.group for x in vertex_groups[i:i+4] ], 0)
        elif elem.name.startswith('BLENDWEIGHT'):
            # TODO: Warn if vertex is in too many vertex groups for this layout
            i = elem.SemanticIndex * 4
            vertex[elem.name] = elem.pad([ x.weight for x in vertex_groups[i:i+4] ], 0.0)
        elif elem.name.startswith('TEXCOORD') and elem.is_float():
            # FIXME: Handle texcoords of other dimensions
            uvs = []
            for uv_name in ('%s.xy' % elem.name, '%s.zw' % elem.name):
                if uv_name in texcoords:
                    uvs += list(texcoords[uv_name][blender_loop_vertex.index])

            vertex[elem.name] = uvs
        else:
            # Unhandled semantics are saved in vertex layers
            data = []
            for component in 'xyzw':
                layer_name = '%s.%s' % (elem.name, component)
                if layer_name in mesh.vertex_layers_int:
                    data.append(mesh.vertex_layers_int[layer_name].data[blender_loop_vertex.vertex_index].value)
                elif layer_name in mesh.vertex_layers_float:
                    data.append(mesh.vertex_layers_float[layer_name].data[blender_loop_vertex.vertex_index].value)
            if data:
                #print('Retrieved unhandled semantic %s %s from vertex layer' % (elem.name, elem.Format), data)
                vertex[elem.name] = data

        if elem.name not in vertex:
            print('NOTICE: Unhandled vertex element: %s' % elem.name)
        #else:
        #    print('%s: %s' % (elem.name, repr(vertex[elem.name])))

    return vertex

def unit_vector(vector):
    a = numpy.linalg.norm(vector, axis=max(len(vector.shape)-1,0), keepdims=True)
    return numpy.divide(vector, a, out=numpy.zeros_like(vector), where= a!=0)

def antiparallel_search(ConnectedFaceNormals):
    a = numpy.einsum('ij,kj->ik', ConnectedFaceNormals, ConnectedFaceNormals)
    return numpy.any((a>-1.000001)&(a<-0.999999))

def precision(x): 
    return -int(numpy.floor(numpy.log10(x)))

def recursive_connections(Over2_connected_points):
    for entry, connectedpointentry in Over2_connected_points.items():
        if len(connectedpointentry & Over2_connected_points.keys()) < 2:
            Over2_connected_points.pop(entry)
            if len(Over2_connected_points) < 3:
                return False
            return recursive_connections(Over2_connected_points)
    return True
    
def checkEnclosedFacesVertex(ConnectedFaces, vg_set, Precalculated_Outline_data):
    
    Main_connected_points = {}
        # connected points non-same vertex
    for face in ConnectedFaces:
        non_vg_points = [p for p in face if p not in vg_set]
        if len(non_vg_points) > 1:
            for point in non_vg_points:
                Main_connected_points.setdefault(point, []).extend([x for x in non_vg_points if x != point])
        # connected points same vertex
    New_Main_connect = {}
    for entry, value in Main_connected_points.items():
        for val in value:
            ivspv = Precalculated_Outline_data.get('Same_Vertex').get(val)-{val}
            intersect_sidevertex = ivspv & Main_connected_points.keys()
            if intersect_sidevertex:
                New_Main_connect.setdefault(entry, []).extend(list(intersect_sidevertex))
        # connected points same vertex reverse connection
    for key, value in New_Main_connect.items():
        Main_connected_points.get(key).extend(value)
        for val in value:
            Main_connected_points.get(val).append(key)
        # exclude for only 2 way paths 
    Over2_connected_points = {k: set(v) for k, v in Main_connected_points.items() if len(v) > 1}

    return recursive_connections(Over2_connected_points)

def blender_vertex_to_3dmigoto_vertex_outline(mesh, obj, blender_loop_vertex, layout, texcoords, export_Outline):
    blender_vertex = mesh.vertices[blender_loop_vertex.vertex_index]
    pos = list(blender_vertex.undeformed_co)
    blp_normal = list(blender_loop_vertex.normal)
    vertex = {}
    seen_offsets = set()

    # TODO: Warn if vertex is in too many vertex groups for this layout,
    # ignoring groups with weight=0.0
    vertex_groups = sorted(blender_vertex.groups, key=lambda x: x.weight, reverse=True)

    for elem in layout:
        if elem.InputSlotClass != 'per-vertex':
            continue

        if (elem.InputSlot, elem.AlignedByteOffset) in seen_offsets:
            continue
        seen_offsets.add((elem.InputSlot, elem.AlignedByteOffset))

        if elem.name == 'POSITION':
            if 'POSITION.w' in mesh.vertex_layers_float:
                vertex[elem.name] = pos + [mesh.vertex_layers_float['POSITION.w'].data[blender_loop_vertex.vertex_index].value]
            else:
                vertex[elem.name] = elem.pad(pos, 1.0)
        elif elem.name.startswith('COLOR'):
            if elem.name in mesh.vertex_colors:
                vertex[elem.name] = elem.clip(list(mesh.vertex_colors[elem.name].data[blender_loop_vertex.index].color))
            else:
                try:
                    vertex[elem.name] = list(mesh.vertex_colors[elem.name+'.RGB'].data[blender_loop_vertex.index].color)[:3] + \
                                            [mesh.vertex_colors[elem.name+'.A'].data[blender_loop_vertex.index].color[0]]
                except KeyError:
                    raise Fatal("ERROR: Unable to find COLOR property. Ensure the model you are exporting has a color attribute (of type Face Corner/Byte Color) called COLOR")
        elif elem.name == 'NORMAL':
            vertex[elem.name] = elem.pad(blp_normal, 0.0)
        elif elem.name.startswith('TANGENT'):
            vertex[elem.name] = elem.pad(export_Outline.get(blender_loop_vertex.vertex_index, blp_normal), blender_loop_vertex.bitangent_sign)
        elif elem.name.startswith('BINORMAL'):
            pass
        elif elem.name.startswith('BLENDINDICES'):
            i = elem.SemanticIndex * 4
            vertex[elem.name] = elem.pad([ x.group for x in vertex_groups[i:i+4] ], 0)
        elif elem.name.startswith('BLENDWEIGHT'):
            # TODO: Warn if vertex is in too many vertex groups for this layout
            i = elem.SemanticIndex * 4
            vertex[elem.name] = elem.pad([ x.weight for x in vertex_groups[i:i+4] ], 0.0)
        elif elem.name.startswith('TEXCOORD') and elem.is_float():
            # FIXME: Handle texcoords of other dimensions
            uvs = []
            for uv_name in ('%s.xy' % elem.name, '%s.zw' % elem.name):
                if uv_name in texcoords:
                    uvs += list(texcoords[uv_name][blender_loop_vertex.index])

            vertex[elem.name] = uvs
        else:
            # Unhandled semantics are saved in vertex layers
            data = []
            for component in 'xyzw':
                layer_name = '%s.%s' % (elem.name, component)
                if layer_name in mesh.vertex_layers_int:
                    data.append(mesh.vertex_layers_int[layer_name].data[blender_loop_vertex.vertex_index].value)
                elif layer_name in mesh.vertex_layers_float:
                    data.append(mesh.vertex_layers_float[layer_name].data[blender_loop_vertex.vertex_index].value)
            if data:
                vertex[elem.name] = data

        if elem.name not in vertex:
            print('NOTICE: Unhandled vertex element: %s' % elem.name)

    return vertex

def write_fmt_file(f, vb, ib):
    f.write('stride: %i\n' % vb.layout.stride)
    f.write('topology: %s\n' % vb.topology)
    if ib is not None:
        f.write('format: %s\n' % ib.format)
    f.write(vb.layout.to_string())

def export_3dmigoto(operator, context, vb_path, ib_path, fmt_path):
    obj = context.object

    if obj is None:
        raise Fatal('No object selected')

    stride = obj['3DMigoto:VBStride']
    layout = InputLayout(obj['3DMigoto:VBLayout'], stride=stride)
    if hasattr(context, "evaluated_depsgraph_get"): # 2.80
        mesh = obj.evaluated_get(context.evaluated_depsgraph_get()).to_mesh()
    else: # 2.79
        mesh = obj.to_mesh(context.scene, True, 'PREVIEW', calc_tessface=False)
    mesh_triangulate(mesh)

    indices = [ l.vertex_index for l in mesh.loops ]
    faces = [ indices[i:i+3] for i in range(0, len(indices), 3) ]
    try:
        if obj['3DMigoto:IBFormat'] == "DXGI_FORMAT_R16_UINT":
            ib_format = "DXGI_FORMAT_R32_UINT"
        else:
            ib_format = obj['3DMigoto:IBFormat']

    except KeyError:
        ib = None
        raise Fatal('FIXME: Add capability to export without an index buffer')
    else:
        ib = IndexBuffer(ib_format)

    # Calculates tangents and makes loop normals valid (still with our
    # custom normal data from import time):
    mesh.calc_tangents()

    texcoord_layers = {}
    for uv_layer in mesh.uv_layers:
        texcoords = {}

        try:
            flip_texcoord_v = obj['3DMigoto:' + uv_layer.name]['flip_v']
            if flip_texcoord_v:
                flip_uv = lambda uv: (uv[0], 1.0 - uv[1])
            else:
                flip_uv = lambda uv: uv
        except KeyError:
            flip_uv = lambda uv: uv

        for l in mesh.loops:
            uv = flip_uv(uv_layer.data[l.index].uv)
            texcoords[l.index] = uv
        texcoord_layers[uv_layer.name] = texcoords

    # Blender's vertices have unique positions, but may have multiple
    # normals, tangents, UV coordinates, etc - these are stored in the
    # loops. To export back to DX we need these combined together such that
    # a vertex is a unique set of all attributes, but we don't want to
    # completely blow this out - we still want to reuse identical vertices
    # via the index buffer. There might be a convenience function in
    # Blender to do this, but it's easy enough to do this ourselves
    indexed_vertices = collections.OrderedDict()
    for poly in mesh.polygons:
        face = []
        for blender_lvertex in mesh.loops[poly.loop_start:poly.loop_start + poly.loop_total]:
            vertex = blender_vertex_to_3dmigoto_vertex(mesh, obj, blender_lvertex, layout, texcoord_layers)
            face.append(indexed_vertices.setdefault(HashableVertex(vertex), len(indexed_vertices)))
        if ib is not None:
            ib.append(face)

    vb = VertexBuffer(layout=layout)
    for vertex in indexed_vertices:
        vb.append(vertex)

    vgmaps = {k[15:]:keys_to_ints(v) for k,v in obj.items() if k.startswith('3DMigoto:VGMap:')}

    if '' not in vgmaps:
        vb.write(open(vb_path, 'wb'), operator=operator)

    base, ext = os.path.splitext(vb_path)
    for (suffix, vgmap) in vgmaps.items():
        path = vb_path
        if suffix:
            path = '%s-%s%s' % (base, suffix, ext)
        vgmap_path = os.path.splitext(path)[0] + '.vgmap'
        print('Exporting %s...' % path)
        vb.remap_blendindices(obj, vgmap)
        vb.write(open(path, 'wb'), operator=operator)
        vb.revert_blendindices_remap()
        sorted_vgmap = collections.OrderedDict(sorted(vgmap.items(), key=lambda x:x[1]))
        json.dump(sorted_vgmap, open(vgmap_path, 'w'), indent=2)

    if ib is not None:
        ib.write(open(ib_path, 'wb'), operator=operator)

    # Write format reference file
    write_fmt_file(open(fmt_path, 'w'), vb, ib)


def export_3dmigoto_genshin(operator, context, object_name, vb_path, ib_path, fmt_path, use_foldername, ignore_hidden, only_selected, no_ramps, delete_intermediate, credit, Outline_Properties):
    scene = bpy.context.scene

    # Quick sanity check
    # If we cannot find any objects in the scene with or any files in the folder with the given name, default to using
    #   the folder name
    if use_foldername or (not [obj for obj in scene.objects if object_name.lower() in obj.name.lower()] \
            or not [file for file in os.listdir(os.path.dirname(vb_path)) if object_name.lower() in file.lower()]):
        object_name = os.path.basename(os.path.dirname(vb_path))
        if not [obj for obj in scene.objects if object_name.lower() in obj.name.lower()] \
            or not [file for file in os.listdir(os.path.dirname(vb_path)) if object_name.lower() in file.lower()]:
                raise Fatal("ERROR: Cannot find match for name. Double check you are exporting as ObjectName.vb to the original data folder, that ObjectName exists in scene and that hash.json exists")

    if "hash.json" in os.listdir(os.path.dirname(vb_path)):
        print("Hash data found in character folder")
        with open(os.path.join(os.path.dirname(vb_path), "hash.json"), "r") as f:
            hash_data = json.load(f)
            all_base_classifications = [x["object_classifications"] for x in hash_data]
            component_names = [x["component_name"] for x in hash_data]
            extended_classifications = [[f"{base_classifications[-1]}{i}" for i in range(2, 10)] for base_classifications in all_base_classifications]

    else:
        print("Hash data not found in character folder, falling back to old behaviour")
        all_base_classifications = [["Head", "Body", "Extra"]]
        component_names = [""]

        extended_classifications = [[f"{base_classifications[-1]}{i}" for i in range(2, 10)] for base_classifications in all_base_classifications]

    for k in range(len(all_base_classifications)):
        base_classifications = all_base_classifications[k]
        current_name = f"{object_name}{component_names[k]}"

        # Doing it this way has the benefit of sorting the objects into the correct ordering by default
        relevant_objects = ["" for i in range(len(base_classifications) + 8)]
        # Surprisingly annoying to extend this to n objects thanks to the choice of using Extra2, Extra3, etc.
        # Iterate through scene objects, looking for ones that match the specified character name and object type

        if only_selected:
            selected_objects = [obj for obj in bpy.context.selected_objects]
        else:
            selected_objects = scene.objects

        for obj in selected_objects:
            print(obj.name.lower())
            #Ignore all hidden meshes while searching if ignore_hidden flag is set
            if ignore_hidden and not obj.visible_get():
                continue
            for i, c in enumerate(base_classifications):
                if f"{current_name}{c}".lower() in obj.name.lower():
                    # Even though we have found an object, since the final classification can be extended need to check
                    found_extended = False
                    for j,d in enumerate(extended_classifications):
                        if f"{current_name}{d}".lower() in obj.name.lower():
                            location = j + len(base_classifications)
                            if relevant_objects[location] != "":
                                raise Fatal(f"Too many matches for {current_name}{d}".lower())
                            else:
                                relevant_objects[location] = obj
                                found_extended = True
                                break
                    if not found_extended:
                        if relevant_objects[i] != "":
                            raise Fatal(f"Too many matches for {current_name}{c}".lower())
                        else:
                            relevant_objects[i] = obj
                            break

        # Delete empty spots
        relevant_objects = [x for x in relevant_objects if x]
        print(relevant_objects)

        for i, obj in enumerate(relevant_objects):
            if i < len(base_classifications):
                classification = base_classifications[i]
            else:
                classification = extended_classifications[i-len(base_classifications)]

            if obj is None:
                raise Fatal('No object selected')

            vb_path  = os.path.join(os.path.dirname(vb_path), current_name + classification + ".vb")
            ib_path  = os.path.join(os.path.dirname(ib_path), current_name + classification + ".ib")
            fmt_path = os.path.join(os.path.dirname(fmt_path), current_name + classification + ".fmt")

            try:
                stride = obj['3DMigoto:VBStride']
            except KeyError:
                raise Fatal("ERROR: Unable to find 3DMigoto:VBStride property, double check the object you are exporting has the custom 3dmigoto properties")
            layout = InputLayout(obj['3DMigoto:VBLayout'], stride=stride)
            if hasattr(context, "evaluated_depsgraph_get"): # 2.80
                mesh = obj.evaluated_get(context.evaluated_depsgraph_get()).to_mesh()
            else: # 2.79
                mesh = obj.to_mesh(context.scene, True, 'PREVIEW', calc_tessface=False)
            mesh_triangulate(mesh)

            try:
                if obj['3DMigoto:IBFormat'] == "DXGI_FORMAT_R16_UINT":
                    ib_format = "DXGI_FORMAT_R32_UINT"
                else:
                    ib_format = obj['3DMigoto:IBFormat']
            except KeyError:
                ib = None
                raise Fatal('FIXME: Add capability to export without an index buffer')
            else:
                ib = IndexBuffer(ib_format)

            if len(mesh.polygons) == 0:
                open(vb_path, 'w').close()
                open(ib_path, 'w').close()
                vb = VertexBuffer(layout=layout)
                write_fmt_file(open(fmt_path, 'w'), vb, ib)

            else:

                indices = [ l.vertex_index for l in mesh.loops ]
                faces = [ indices[i:i+3] for i in range(0, len(indices), 3) ]

                # Calculates tangents and makes loop normals valid (still with our
                # custom normal data from import time):
                try:
                    mesh.calc_tangents()
                except RuntimeError:
                    raise Fatal ("ERROR: Unable to find UV map. Double check UV map exists and is called TEXCOORD.xy")


                texcoord_layers = {}
                count = 0
                for uv_layer in mesh.uv_layers:
                    texcoords = {}
                    uvname = uv_layer.name
                    if "TEXCOORD" not in uv_layer.name:
                        if count == 0:
                            uvname = "TEXCOORD.xy"
                        else:
                            uvname = f"TEXCOORD{count}.xy"
                    try:
                        flip_texcoord_v = obj['3DMigoto:' + uvname]['flip_v']
                        if flip_texcoord_v:
                            flip_uv = lambda uv: (uv[0], 1.0 - uv[1])
                        else:
                            flip_uv = lambda uv: uv
                    except KeyError:
                        flip_uv = lambda uv: uv

                    for l in mesh.loops:
                        uv = flip_uv(uv_layer.data[l.index].uv)
                        texcoords[l.index] = uv
                    texcoord_layers[uvname] = texcoords
                    count += 1

                # Blender's vertices have unique positions, but may have multiple
                # normals, tangents, UV coordinates, etc - these are stored in the
                # loops. To export back to DX we need these combined together such that
                # a vertex is a unique set of all attributes, but we don't want to
                # completely blow this out - we still want to reuse identical vertices
                # via the index buffer. There might be a convenience function in
                # Blender to do this, but it's easy enough to do this ourselves

                indexed_vertices = collections.OrderedDict()
                Precalculated_Outline_data = {}
                export_Outline = {}
                outline_optimization, toggle_rounding_outline, decimal_rounding_outline, angle_weighted, overlapping_faces, detect_edges, calculate_all_faces, nearest_edge_distance = Outline_Properties

                if outline_optimization:
                    print("Optimize Outline: " + obj.name.lower() + "; Initialize data sets         ", end='\r')

                    ################# PRE-DICTIONARY #####################

                    verts_obj = mesh.vertices
                    Pos_Same_Vertices = {}
                    Pos_Close_Vertices = {}
                    Face_Verts = {}
                    Face_Normals = {}
                    Numpy_Position = {}
                    if detect_edges and toggle_rounding_outline:
                        i_nedd = min(precision(nearest_edge_distance), decimal_rounding_outline) - 1
                        i_nedd_increment =  10**(-i_nedd)
                    
                    searched_vertex_pos = set()
                    for poly in mesh.polygons:
                        i_poly = poly.index
                        face_vertices = poly.vertices
                        facenormal = numpy.array(poly.normal)
                        Face_Verts.setdefault(i_poly, face_vertices)
                        Face_Normals.setdefault(i_poly, facenormal)

                        for vert in face_vertices:
                            Precalculated_Outline_data.setdefault('Connected_Faces', {}).setdefault(vert, []).append(i_poly)
                            if vert in searched_vertex_pos: continue

                            searched_vertex_pos.add(vert)
                            vert_obj = verts_obj[vert]
                            vert_position = vert_obj.undeformed_co
                            
                            if toggle_rounding_outline:
                                Pos_Same_Vertices.setdefault(tuple(round(coord, decimal_rounding_outline) for coord in vert_position), set()).add(vert)
                                
                                if detect_edges:
                                    Pos_Close_Vertices.setdefault(tuple(round(coord, i_nedd) for coord in vert_position), set()).add(vert)
                            else:
                                Pos_Same_Vertices.setdefault(tuple(vert_position), set()).add(vert)

                            if angle_weighted:
                                numpy_pos = numpy.array(vert_position)
                                Numpy_Position.setdefault(vert, numpy_pos)

                    for values in Pos_Same_Vertices.values():
                        for vertex in values:
                            Precalculated_Outline_data.setdefault('Same_Vertex', {}).setdefault(vertex, set(values))

                    if detect_edges and toggle_rounding_outline:
                        print("Optimize Outline: " + obj.name.lower() + "; Edge detection       ", end='\r')
                        Precalculated_Outline_data.setdefault('RepositionLocal', set())

                        for vertex_group in Pos_Same_Vertices.values():
                            FacesConnected = []
                            for x in vertex_group: FacesConnected.extend(Precalculated_Outline_data.get('Connected_Faces').get(x))
                            ConnectedFaces = [Face_Verts.get(x) for x in FacesConnected]
                            
                            if not checkEnclosedFacesVertex(ConnectedFaces, vertex_group, Precalculated_Outline_data):
                                for vertex in vertex_group: break

                                p1, p2, p3 = verts_obj[vertex].undeformed_co
                                p1n = p1+nearest_edge_distance
                                p1nn = p1-nearest_edge_distance
                                p2n = p2+nearest_edge_distance
                                p2nn = p2-nearest_edge_distance
                                p3n = p3+nearest_edge_distance
                                p3nn = p3-nearest_edge_distance

                                coord = [[round(p1n, i_nedd), round(p1nn, i_nedd)],\
                                         [round(p2n, i_nedd), round(p2nn, i_nedd)],\
                                         [round(p3n, i_nedd), round(p3nn, i_nedd)]]

                                for i in range(3):
                                    z, n = coord[i]
                                    zndifference = int((z - n)/i_nedd_increment)
                                    if zndifference > 1: 
                                        for r in range(zndifference - 1):
                                            coord[i].append(z - r*i_nedd_increment)

                                closest_group = set()
                                for pos1 in coord[0]:
                                    for pos2 in coord[1]:
                                        for pos3 in coord[2]:
                                            try: closest_group.update(Pos_Close_Vertices.get((pos1, pos2, pos3)))
                                            except: continue

                                if len(closest_group) != 1:
                                    for x in vertex_group: Precalculated_Outline_data.get('RepositionLocal').add(x)
                                                
                                    for v_closest_pos in closest_group:
                                        if not v_closest_pos in vertex_group:

                                            o1, o2, o3 = verts_obj[v_closest_pos].undeformed_co
                                            if p1n >= o1 >= p1nn and p2n >= o2 >= p2nn and p3n >= o3 >= p3nn:
                                                for x in vertex_group:
                                                    Precalculated_Outline_data.get('Same_Vertex').get(x).add(v_closest_pos)

                    Connected_Faces_bySameVertex = {}
                    for key, value in Precalculated_Outline_data.get('Same_Vertex').items():
                        for vertex in value:
                            Connected_Faces_bySameVertex.setdefault(key, set()).update(Precalculated_Outline_data.get('Connected_Faces').get(vertex))

                    ################# CALCULATIONS #####################

                    RepositionLocal = Precalculated_Outline_data.get('RepositionLocal')
                    IteratedValues = set()
                    print("Optimize Outline: " + obj.name.lower() + "; Calculation          ", end='\r')

                    for key, vertex_group in Precalculated_Outline_data.get('Same_Vertex').items():
                        if key in IteratedValues: continue

                        if not calculate_all_faces and len(vertex_group) == 1: continue
                        
                        FacesConnectedbySameVertex = list(Connected_Faces_bySameVertex.get(key))
                        row = len(FacesConnectedbySameVertex)
                        
                        if overlapping_faces:
                            ConnectedFaceNormals = numpy.empty(shape=(row,3))
                            for i_normal, x in enumerate(FacesConnectedbySameVertex):
                                ConnectedFaceNormals[i_normal] = Face_Normals.get(x)
                            if antiparallel_search(ConnectedFaceNormals): continue

                        if angle_weighted:
                            VectorMatrix0 = numpy.empty(shape=(row,3))
                            VectorMatrix1 = numpy.empty(shape=(row,3))

                        ConnectedWeightedNormal = numpy.empty(shape=(row,3))
                        i = 0
                        for facei in FacesConnectedbySameVertex:
                            vlist = Face_Verts.get(facei)
                            
                            vert0p = set(vlist) & vertex_group

                            if angle_weighted:
                                for vert0 in vert0p:
                                    v0 = Numpy_Position.get(vert0)
                                    vn = [Numpy_Position.get(x) for x in vlist if x != vert0]
                                    VectorMatrix0[i] = vn[0]-v0
                                    VectorMatrix1[i] = vn[1]-v0   
                            ConnectedWeightedNormal[i] = Face_Normals.get(facei) 

                            influence_restriction = len(vert0p)
                            if  influence_restriction > 1:
                                numpy.multiply(ConnectedWeightedNormal[i], 0.5**(1-influence_restriction))
                            i += 1

                        if angle_weighted:
                            angle = numpy.arccos(numpy.clip(numpy.einsum('ij, ij->i',\
                                    unit_vector(VectorMatrix0), unit_vector(VectorMatrix1)), -1.0, 1.0))
                            ConnectedWeightedNormal *= angle[:,None]

                        wSum = unit_vector(numpy.sum(ConnectedWeightedNormal,axis=0)).tolist()

                        if wSum != [0,0,0]:
                            if RepositionLocal and key in RepositionLocal:
                                export_Outline.setdefault(key, wSum)
                                continue
                            for vertexf in vertex_group:
                                export_Outline.setdefault(vertexf, wSum)
                                IteratedValues.add(vertexf)
                    print("Optimize Outline: " + obj.name.lower() + "; Completed            ")

                    for poly in mesh.polygons:
                        face = []
                        for blender_lvertex in mesh.loops[poly.loop_start:poly.loop_start + poly.loop_total]:
                            vertex = blender_vertex_to_3dmigoto_vertex_outline(mesh, obj, blender_lvertex, layout, texcoord_layers, export_Outline)
                            face.append(indexed_vertices.setdefault(HashableVertex(vertex), len(indexed_vertices)))           
                        if ib is not None:
                            ib.append(face)

                else:
                
                    for poly in mesh.polygons:
                        face = []
                        for blender_lvertex in mesh.loops[poly.loop_start:poly.loop_start + poly.loop_total]:
                            vertex = blender_vertex_to_3dmigoto_vertex(mesh, obj, blender_lvertex, layout, texcoord_layers)
                            face.append(indexed_vertices.setdefault(HashableVertex(vertex), len(indexed_vertices)))
                        if ib is not None:
                            ib.append(face)

                vb = VertexBuffer(layout=layout)
                for vertex in indexed_vertices:
                    vb.append(vertex)

                vgmaps = {k[15:]:keys_to_ints(v) for k,v in obj.items() if k.startswith('3DMigoto:VGMap:')}

                if '' not in vgmaps:
                    vb.write(open(vb_path, 'wb'), operator=operator)

                base, ext = os.path.splitext(vb_path)
                for (suffix, vgmap) in vgmaps.items():
                    path = vb_path
                    if suffix:
                        path = '%s-%s%s' % (base, suffix, ext)
                    vgmap_path = os.path.splitext(path)[0] + '.vgmap'
                    print('Exporting %s...' % path)
                    vb.remap_blendindices(obj, vgmap)
                    vb.write(open(path, 'wb'), operator=operator)
                    vb.revert_blendindices_remap()
                    sorted_vgmap = collections.OrderedDict(sorted(vgmap.items(), key=lambda x:x[1]))
                    json.dump(sorted_vgmap, open(vgmap_path, 'w'), indent=2)

                if ib is not None:
                    ib.write(open(ib_path, 'wb'), operator=operator)

                # Write format reference file
                write_fmt_file(open(fmt_path, 'w'), vb, ib)

    generate_mod_folder(os.path.dirname(vb_path), object_name, no_ramps, delete_intermediate, credit)


def generate_mod_folder(path, character_name, no_ramps, delete_intermediate, credit):

    parent_folder = os.path.join(path, "../")

    char_hash = load_hashes(path, character_name, "hash.json")
    create_mod_folder(parent_folder, character_name)

    # Previous version had all these hardcoded at the end; now, we dynamically assemble the ini file as we add components
    vb_override_ini = ""
    ib_override_ini = ""
    vb_res_ini = ""
    ib_res_ini = ""
    tex_res_ini = ""

    for component in char_hash:

        # Support for custom names was added so we need this to retain backwards compatibility
        if "component_name" in component:
            component_name = component["component_name"]
        else:
            component_name = ""

        # Old version used "Extra" as the third object, but I've replaced it with dress - need this for backwards compatibility
        if "object_classifications" in component:
            object_classifications = component["object_classifications"]
        else:
            object_classifications = ["Head", "Body", "Extra"]

        current_name = f"{character_name}{component_name}"

        print(f"\nWorking on {current_name}")

        # Components without draw vbs are texture overrides only
        if component["draw_vb"]:

            with open(os.path.join(path, f"{current_name}{object_classifications[0]}.fmt"), "r") as f:
                stride = int([x.split(": ")[1] for x in f.readlines() if "stride:" in x][0])

            offset = 0
            position, blend, texcoord = bytearray(), bytearray(), bytearray()
            ib_override_ini += f"[TextureOverride{current_name}IB]\nhash = {component['ib']}\nhandling = skip\ndrawindexed = auto\n\n"
            for i in range(len(component["object_indexes"])):
                if i + 1 > len(object_classifications):current_object = f"{object_classifications[-1]}{i + 2 - len(object_classifications)}"
                else:
                    current_object = object_classifications[i]

                print(f"\nCollecting {current_object}")

                # This is the path for components which have blend data (characters, complex weapons, etc.)
                if component["blend_vb"]:
                    print("Splitting VB by buffer type, merging body parts")
                    try:
                        x, y, z = collect_vb(path, current_name, current_object, stride)
                    except:
                        raise Fatal(f"ERROR: Unable to find {current_name} {current_object} when exporting. Double check the object exists and is named correctly")
                    position += x
                    blend += y
                    texcoord += z
                    position_stride = 40

                # This is the path for components without blend data (simple weapons, objects, etc.)
                # Simplest route since we do not need to split up the buffer into multiple components
                else:
                    position += collect_vb_single(path, current_name, current_object, stride)
                    position_stride = stride

                if delete_intermediate:
                    os.remove(os.path.join(path, f"{current_name}{current_object}.vb"))

                print("Collecting IB")
                print(current_name, current_object, offset)
                ib = collect_ib(path, current_name, current_object, offset)

                if delete_intermediate:
                    os.remove(os.path.join(path, f"{current_name}{current_object}.ib"))

                with open(os.path.join(parent_folder, f"{character_name}Mod", f"{current_name}{current_object}.ib"), "wb") as f:
                    f.write(ib)
                if ib:
                    ib_override_ini += f"[TextureOverride{current_name}{current_object}]\nhash = {component['ib']}\nmatch_first_index = {component['object_indexes'][i]}\nib = Resource{current_name}{current_object}IB\n"
                else:
                    ib_override_ini += f"[TextureOverride{current_name}{current_object}]\nhash = {component['ib']}\nmatch_first_index = {component['object_indexes'][i]}\nib = null\n"
                ib_res_ini += f"[Resource{current_name}{current_object}IB]\ntype = Buffer\nformat = DXGI_FORMAT_R32_UINT\nfilename = {current_name}{current_object}.ib\n\n"

                if delete_intermediate:
                    os.remove(os.path.join(path, f"{current_name}{current_object}.fmt"))

                if len(position) % position_stride != 0:
                    print("ERROR: VB buffer length does not match stride")

                offset = len(position) // position_stride

                # Older versions can only manage diffuse and lightmaps
                if "texture_hashes" in component:
                    texture_hashes = component["texture_hashes"][i]
                else:
                    texture_hashes = [["Diffuse", ".dds", "_"], ["LightMap", ".dds", "_"]]

                print("Copying texture files")
                if component["component_name"] == "Face":
                    j = 0
                    texture = texture_hashes[j]
                    ib_override_ini += f"[TextureOverride{current_name}{current_object}{texture[0]}]\nhash = {texture[2]}\n"
                    shutil.copy(os.path.join(path, f"{current_name}{current_object}{texture[0]}{texture[1]}"),
                                os.path.join(parent_folder, f"{character_name}Mod", f"{current_name}{current_object}{texture[0]}{texture[1]}"))
                    ib_override_ini += f"ps-t{j} = Resource{current_name}{current_object}{texture[0]}\n"
                    tex_res_ini += f"[Resource{current_name}{current_object}{texture[0]}]\nfilename = {current_name}{current_object}{texture[0]}{texture[1]}\n\n"
                else:
                    for j, texture in enumerate(texture_hashes):
                        if no_ramps and texture[0] in ["ShadowRamp", "MetalMap", "DiffuseGuide"]:
                            continue
                        shutil.copy(os.path.join(path, f"{current_name}{current_object}{texture[0]}{texture[1]}"),
                                    os.path.join(parent_folder, f"{character_name}Mod",f"{current_name}{current_object}{texture[0]}{texture[1]}"))
                        ib_override_ini += f"ps-t{j} = Resource{current_name}{current_object}{texture[0]}\n"
                        tex_res_ini += f"[Resource{current_name}{current_object}{texture[0]}]\nfilename = {current_name}{current_object}{texture[0]}{texture[1]}\n\n"
                ib_override_ini += "\n"

            if component["blend_vb"]:
                print("Writing merged buffer files")
                with open(os.path.join(parent_folder, f"{character_name}Mod", f"{current_name}Position.buf"), "wb") as f, \
                        open(os.path.join(parent_folder, f"{character_name}Mod", f"{current_name}Blend.buf"), "wb") as g, \
                        open(os.path.join(parent_folder, f"{character_name}Mod", f"{current_name}Texcoord.buf"), "wb") as h:
                    f.write(position)
                    g.write(blend)
                    h.write(texcoord)

                vb_override_ini += f"[TextureOverride{current_name}Position]\nhash = {component['position_vb']}\nvb0 = Resource{current_name}Position\n"
                if credit:
                    vb_override_ini += "$active = 1\n"
                vb_override_ini += "\n"
                vb_override_ini += f"[TextureOverride{current_name}Blend]\nhash = {component['blend_vb']}\nvb1 = Resource{current_name}Blend\nhandling = skip\ndraw = {len(position) // 40},0 \n\n"
                vb_override_ini += f"[TextureOverride{current_name}Texcoord]\nhash = {component['texcoord_vb']}\nvb1 = Resource{current_name}Texcoord\n\n"
                vb_override_ini += f"[TextureOverride{current_name}VertexLimitRaise]\nhash = {component['draw_vb']}\n\n"

                vb_res_ini += f"[Resource{current_name}Position]\ntype = Buffer\nstride = 40\nfilename = {current_name}Position.buf\n\n"
                vb_res_ini += f"[Resource{current_name}Blend]\ntype = Buffer\nstride = 32\nfilename = {current_name}Blend.buf\n\n"
                vb_res_ini += f"[Resource{current_name}Texcoord]\ntype = Buffer\nstride = {stride - 72}\nfilename = {current_name}Texcoord.buf\n\n"
            else:
                with open(os.path.join(parent_folder, f"{character_name}Mod", f"{current_name}.buf"), "wb") as f:
                    f.write(position)
                vb_override_ini += f"[TextureOverride{current_name}]\nhash = {component['draw_vb']}\nvb0 = Resource{current_name}\n"
                if credit:
                    vb_override_ini += "$active = 1\n"
                vb_override_ini += "\n"
                vb_res_ini += f"[Resource{current_name}]\ntype = Buffer\nstride = {stride}\nfilename = {current_name}.buf\n\n"


        # This is the path for components with only texture overrides (faces, wings, etc.)
        # Theoretically possible to combine with the above to cut down on code, but results in lots of messy if statements
        else:
            for i in range(len(component["object_indexes"])):
                if i > 2:
                    current_object = f"{object_classifications[2]}{i - 1}"
                else:
                    current_object = object_classifications[i]

                print(f"\nTexture override only on {current_object}")

                if component["texture_hashes"]:
                    texture_hashes = component["texture_hashes"][i]
                else:
                    texture_hashes = [{"Diffuse": "_"}, {"LightMap": "_"}]

                print("Copying texture files")
                if component["component_name"] == "Face":
                    j = 0
                    texture = texture_hashes[j]
                    ib_override_ini += f"[TextureOverride{current_name}{current_object}{texture[0]}]\nhash = {texture[2]}\n"
                    shutil.copy(os.path.join(path, f"{current_name}{current_object}{texture[0]}{texture[1]}"),
                                os.path.join(parent_folder, f"{character_name}Mod",f"{current_name}{current_object}{texture[0]}{texture[1]}"))
                    ib_override_ini += f"ps-t{j} = Resource{current_name}{current_object}{texture[0]}\n\n"
                    tex_res_ini += f"[Resource{current_name}{current_object}{texture[0]}]\nfilename = {current_name}{current_object}{texture[0]}{texture[1]}\n\n"
                else:
                    for j, texture in enumerate(texture_hashes):
                        if no_ramps and texture[0] in ["ShadowRamp", "MetalMap", "DiffuseGuide"]:
                            continue
                        ib_override_ini += f"[TextureOverride{current_name}{current_object}{texture[0]}]\nhash = {texture[2]}\n"
                        shutil.copy(os.path.join(path, f"{current_name}{current_object}{texture[0]}{texture[1]}"),
                                    os.path.join(parent_folder, f"{character_name}Mod",f"{current_name}{current_object}{texture[0]}{texture[1]}"))
                        ib_override_ini += f"ps-t{j} = Resource{current_name}{current_object}{texture[0]}\n\n"
                        tex_res_ini += f"[Resource{current_name}{current_object}{texture[0]}]\nfilename = {current_name}{current_object}{texture[0]}{texture[1]}\n\n"
                ib_override_ini += "\n"

    constant_ini = ""
    command_ini = ""
    other_res = ""
    if credit:
        constant_ini += f"[Constants]\nglobal $active = 0\nglobal $creditinfo = 0\n\n[Present]\npost $active = 0\nrun = CommandListCreditInfo\n\n"
        command_ini += "[CommandListCreditInfo]\nif $creditinfo == 0 && $active == 1\n" \
                       "\tpre Resource\\ShaderFixes\\help.ini\\Notification = ResourceCreditInfo\n" \
                       "\tpre run = CustomShader\\ShaderFixes\\help.ini\\FormatText\n" \
                       "\tpre $\\ShaderFixes\\help.ini\\notification_timeout = time + 5.0\n" \
                       "\t$creditinfo = 1\n" \
                       "endif\n\n"
        other_res += f'[ResourceCreditInfo]\ntype = Buffer\ndata = "Created by {credit}"\n\n'

    print("Generating .ini file")
    ini_data = f"; {character_name}\n\n"
    ini_data += f"; Constants -------------------------\n\n" + constant_ini
    ini_data += f"; Overrides -------------------------\n\n" + vb_override_ini + ib_override_ini
    ini_data += f"; CommandList -----------------------\n\n" + command_ini
    ini_data += f"; Resources -------------------------\n\n" + vb_res_ini + ib_res_ini + tex_res_ini + other_res
    ini_data += f"\n; .ini generated by GIMI (Genshin-Impact-Model-Importer)\n" \
        f"; If you have any issues or find any bugs, please open a ticket at https://github.com/SilentNightSound/GI-Model-Importer/issues or contact SilentNightSound#7430 on discord"

    with open(os.path.join(parent_folder, f"{character_name}Mod", f"{character_name}.ini"), "w") as f:
        print("Writing ini file")
        f.write(ini_data)

    print("All operations completed, exiting")


def load_hashes(path, name, hashfile):
    parent_folder = os.path.join(path, "../")
    if hashfile not in os.listdir(path):
        print("WARNING: Could not find hash.info in character directory. Falling back to hash_info.json")
        if "hash_info.json" not in os.listdir(parent_folder):
            raise Fatal("Cannot find hash information, check hash.json in folder")
        # Backwards compatibility with the old hash_info.json
        with open(os.path.join(parent_folder, "hash_info.json"), "r") as f:
            hash_data = json.load(f)
            char_hashes = [hash_data[name]]
    else:
        with open(os.path.join(path, hashfile), "r") as f:
            char_hashes = json.load(f)

    return char_hashes


def create_mod_folder(parent_folder, name):
    if not os.path.isdir(os.path.join(parent_folder, f"{name}Mod")):
        print(f"Creating {name}Mod")
        os.mkdir(os.path.join(parent_folder, f"{name}Mod"))
    else:
        print(f"WARNING: Everything currently in the {name}Mod folder will be overwritten - make sure any important files are backed up. Press any button to continue")

def collect_vb(folder, name, classification, stride): 
    position = bytearray()
    blend = bytearray()
    texcoord = bytearray()
    with open(os.path.join(folder, f"{name}{classification}.vb"), "rb") as f:
        data = f.read()
        data = bytearray(data)
        i = 0
        while i < len(data):
            import binascii
            position += data[i:i+40]
            blend += data[i+40:i+72]
            texcoord += data[i+72:i+stride]
            i += stride
    return position, blend, texcoord


def collect_ib(folder, name, classification, offset):
    ib = bytearray()
    with open(os.path.join(folder, f"{name}{classification}.ib"), "rb") as f:
        data = f.read()
        data = bytearray(data)
        i = 0
        while i < len(data):
            ib += struct.pack('1I', struct.unpack('1I', data[i:i+4])[0]+offset)
            i += 4
    return ib


def collect_vb_single(folder, name, classification, stride): 
    result = bytearray()
    with open(os.path.join(folder, f"{name}{classification}.vb"), "rb") as f:
        data = f.read()
        data = bytearray(data)
        i = 0
        while i < len(data):
            result += data[i:i+stride]
            i += stride
    return result


# Parsing the headers for vb0 txt files
# This has been constructed by the collect script, so its headers are much more accurate than the originals
def parse_buffer_headers(headers, filters):
    results = []
    # https://docs.microsoft.com/en-us/windows/win32/api/dxgiformat/ne-dxgiformat-dxgi_format
    for element in headers.split("]:")[1:]:
        lines = element.strip().splitlines()
        name = lines[0].split(": ")[1]
        index = lines[1].split(": ")[1]
        data_format = lines[2].split(": ")[1]
        bytewidth = sum([int(x) for x in re.findall("([0-9]*)[^0-9]", data_format.split("_")[0]+"_") if x])//8

        # A bit annoying, but names can be very similar so need to match filter format exactly
        element_name = name
        if index != "0":
            element_name += index
        if element_name+":" not in filters:
            continue

        results.append({"semantic_name": name, "element_name": element_name, "index": index, "format": data_format, "bytewidth": bytewidth})

    return results


@orientation_helper(axis_forward='-Z', axis_up='Y')
class Import3DMigotoFrameAnalysis(bpy.types.Operator, ImportHelper, IOOBJOrientationHelper):
    """Import a mesh dumped with 3DMigoto's frame analysis"""
    bl_idname = "import_mesh.migoto_frame_analysis"
    bl_label = "Import 3DMigoto Frame Analysis Dump"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = '.txt'
    filter_glob : StringProperty(
            default='*.txt',
            options={'HIDDEN'},
            )

    files : CollectionProperty(
            name="File Path",
            type=bpy.types.OperatorFileListElement,
            )

    flip_texcoord_v : BoolProperty(
            name="Flip TEXCOORD V",
            description="Flip TEXCOORD V asix during importing",
            default=True,
            )

    load_related : BoolProperty(
            name="Auto-load related meshes",
            description="Automatically load related meshes found in the frame analysis dump",
            default=True,
            )

    load_buf : BoolProperty(
            name="Load .buf files instead",
            description="Load the mesh from the binary .buf dumps instead of the .txt files\nThis will load the entire mesh as a single object instead of separate objects from each draw call",
            default=False,
            )

    merge_meshes : BoolProperty(
            name="Merge meshes together",
            description="Merge all selected meshes together into one object. Meshes must be related",
            default=False,
            )

    pose_cb : StringProperty(
            name="Bone CB",
            description='Indicate a constant buffer slot (e.g. "vs-cb2") containing the bone matrices',
            default="",
            )

    pose_cb_off : bpy.props.IntVectorProperty(
            name="Bone CB range",
            description='Indicate start and end offsets (in multiples of 4 component values) to find the matrices in the Bone CB',
            default=[0,0],
            size=2,
            min=0,
            )

    pose_cb_step : bpy.props.IntProperty(
            name="Vertex group step",
            description='If used vertex groups are 0,1,2,3,etc specify 1. If they are 0,3,6,9,12,etc specify 3',
            default=1,
            min=1,
            )

    def get_vb_ib_paths(self):
        buffer_pattern = re.compile(r'''-(?:ib|vb[0-9]+)(?P<hash>=[0-9a-f]+)?(?=[^0-9a-f=])''')

        dirname = os.path.dirname(self.filepath)
        ret = set()

        files = []
        if self.load_related:
            for filename in self.files:
                match = buffer_pattern.search(filename.name)
                if match is None or not match.group('hash'):
                    continue
                paths = glob(os.path.join(dirname, '*%s*.txt' % filename.name[match.start():match.end()]))
                files.extend([os.path.basename(x) for x in paths])
        if not files:
            files = [x.name for x in self.files]

        for filename in files:
            match = buffer_pattern.search(filename)
            if match is None:
                raise Fatal('Unable to find corresponding buffers from filename - ensure you are loading a dump from a timestamped Frame Analysis directory (not a deduped directory)')

            use_bin = self.load_buf
            if not match.group('hash') and not use_bin:
                self.report({'INFO'}, 'Filename did not contain hash - if Frame Analysis dumped a custom resource the .txt file may be incomplete, Using .buf files instead')
                use_bin = True # FIXME: Ask

            ib_pattern = filename[:match.start()] + '-ib*' + filename[match.end():]
            vb_pattern = filename[:match.start()] + '-vb*' + filename[match.end():]
            ib_paths = glob(os.path.join(dirname, ib_pattern))
            vb_paths = glob(os.path.join(dirname, vb_pattern))

            if vb_paths and use_bin:
                vb_bin_paths = [ os.path.splitext(x)[0] + '.buf' for x in vb_paths ]
                ib_bin_paths = [ os.path.splitext(x)[0] + '.buf' for x in ib_paths ]
                if all([ os.path.exists(x) for x in itertools.chain(vb_bin_paths, ib_bin_paths) ]):
                    # When loading the binary files, we still need to process
                    # the .txt files as well, as they indicate the format:
                    ib_paths = list(zip(ib_bin_paths, ib_paths))
                    vb_paths = list(zip(vb_bin_paths, vb_paths))
                else:
                    self.report({'WARNING'}, 'Corresponding .buf files not found - using .txt files')
                    use_bin = False

            pose_path = None
            if self.pose_cb:
                pose_pattern = filename[:match.start()] + '*-' + self.pose_cb + '=*.txt'
                try:
                    pose_path = glob(os.path.join(dirname, pose_pattern))[0]
                except IndexError:
                    pass

            if len(ib_paths) != 1 or len(vb_paths) != 1:
                raise Fatal('Only draw calls using a single vertex buffer and a single index buffer are supported for now')
            ret.add((vb_paths[0], ib_paths[0], use_bin, pose_path))
        return ret

    def execute(self, context):
        if self.load_buf:
            # Is there a way to have the mutual exclusivity reflected in
            # the UI? Grey out options or use radio buttons or whatever?
            if self.merge_meshes or self.load_related:
                self.report({'INFO'}, 'Loading .buf files selected: Disabled incompatible options')
            self.merge_meshes = False
            self.load_related = False

        try:
            keywords = self.as_keywords(ignore=('filepath', 'files', 'filter_glob', 'load_related', 'load_buf', 'pose_cb'))
            paths = self.get_vb_ib_paths()

            import_3dmigoto(self, context, paths, **keywords)
        except Fatal as e:
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}

def import_3dmigoto_raw_buffers(operator, context, vb_fmt_path, ib_fmt_path, vb_path=None, ib_path=None, vgmap_path=None, **kwargs):
    paths = (((vb_path, vb_fmt_path), (ib_path, ib_fmt_path), True, None),)
    obj = import_3dmigoto(operator, context, paths, merge_meshes=False, **kwargs)
    if obj and vgmap_path:
        apply_vgmap(operator, context, targets=obj, filepath=vgmap_path, rename=True, cleanup=True)

@orientation_helper(axis_forward='-Z', axis_up='Y')
class Import3DMigotoRaw(bpy.types.Operator, ImportHelper, IOOBJOrientationHelper):
    """Import raw 3DMigoto vertex and index buffers"""
    bl_idname = "import_mesh.migoto_raw_buffers"
    bl_label = "Import 3DMigoto Raw Buffers"
    #bl_options = {'PRESET', 'UNDO'}
    bl_options = {'UNDO'}

    filename_ext = '.vb;.ib'
    filter_glob : StringProperty(
            default='*.vb;*.ib',
            options={'HIDDEN'},
            )

    files : CollectionProperty(
            name="File Path",
            type=bpy.types.OperatorFileListElement,
            )

    flip_texcoord_v : BoolProperty(
            name="Flip TEXCOORD V",
            description="Flip TEXCOORD V asix during importing",
            default=True,
            )

    def get_vb_ib_paths(self, filename):
        vb_bin_path = os.path.splitext(filename)[0] + '.vb'
        ib_bin_path = os.path.splitext(filename)[0] + '.ib'
        fmt_path = os.path.splitext(filename)[0] + '.fmt'
        vgmap_path = os.path.splitext(filename)[0] + '.vgmap'
        if not os.path.exists(vb_bin_path):
            raise Fatal('Unable to find matching .vb file for %s' % filename)
        if not os.path.exists(ib_bin_path):
            raise Fatal('Unable to find matching .ib file for %s' % filename)
        if not os.path.exists(fmt_path):
            fmt_path = None
        if not os.path.exists(vgmap_path):
            vgmap_path = None
        return (vb_bin_path, ib_bin_path, fmt_path, vgmap_path)

    def execute(self, context):
        # I'm not sure how to find the Import3DMigotoReferenceInputFormat
        # instance that Blender instantiated to pass the values from one
        # import dialog to another, but since everything is modal we can
        # just use globals:
        global migoto_raw_import_options
        migoto_raw_import_options = self.as_keywords(ignore=('filepath', 'files', 'filter_glob'))

        done = set()
        dirname = os.path.dirname(self.filepath)
        for filename in self.files:
            try:
                (vb_path, ib_path, fmt_path, vgmap_path) = self.get_vb_ib_paths(os.path.join(dirname, filename.name))
                if os.path.normcase(vb_path) in done:
                    continue
                done.add(os.path.normcase(vb_path))

                if fmt_path is not None:
                    import_3dmigoto_raw_buffers(self, context, fmt_path, fmt_path, vb_path=vb_path, ib_path=ib_path, vgmap_path=vgmap_path, **migoto_raw_import_options)
                else:
                    migoto_raw_import_options['vb_path'] = vb_path
                    migoto_raw_import_options['ib_path'] = ib_path
                    bpy.ops.import_mesh.migoto_input_format('INVOKE_DEFAULT')
            except Fatal as e:
                self.report({'ERROR'}, str(e))
        return {'FINISHED'}

class Import3DMigotoReferenceInputFormat(bpy.types.Operator, ImportHelper):
    bl_idname = "import_mesh.migoto_input_format"
    bl_label = "Select a .txt file with matching format"
    bl_options = {'UNDO', 'INTERNAL'}

    filename_ext = '.txt;.fmt'
    filter_glob : StringProperty(
            default='*.txt;*.fmt',
            options={'HIDDEN'},
            )

    def get_vb_ib_paths(self):
        if os.path.splitext(self.filepath)[1].lower() == '.fmt':
            return (self.filepath, self.filepath)

        buffer_pattern = re.compile(r'''-(?:ib|vb[0-9]+)(?P<hash>=[0-9a-f]+)?(?=[^0-9a-f=])''')

        dirname = os.path.dirname(self.filepath)
        filename = os.path.basename(self.filepath)

        match = buffer_pattern.search(filename)
        if match is None:
            raise Fatal('Reference .txt filename does not look like a 3DMigoto timestamped Frame Analysis Dump')
        ib_pattern = filename[:match.start()] + '-ib*' + filename[match.end():]
        vb_pattern = filename[:match.start()] + '-vb*' + filename[match.end():]
        ib_paths = glob(os.path.join(dirname, ib_pattern))
        vb_paths = glob(os.path.join(dirname, vb_pattern))
        if len(ib_paths) < 1 or len(vb_paths) < 1:
            raise Fatal('Unable to locate reference files for both vertex buffer and index buffer format descriptions')
        return (vb_paths[0], ib_paths[0])

    def execute(self, context):
        global migoto_raw_import_options

        try:
            vb_fmt_path, ib_fmt_path = self.get_vb_ib_paths()
            import_3dmigoto_raw_buffers(self, context, vb_fmt_path, ib_fmt_path, **migoto_raw_import_options)
        except Fatal as e:
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}

class Export3DMigoto(bpy.types.Operator, ExportHelper):
    """Export a mesh for re-injection into a game with 3DMigoto"""
    bl_idname = "export_mesh.migoto"
    bl_label = "Export 3DMigoto Vertex & Index Buffers"

    filename_ext = '.vb'
    filter_glob : StringProperty(
            default='*.vb',
            options={'HIDDEN'},
            )

    def execute(self, context):
        try:
            vb_path = self.filepath
            ib_path = os.path.splitext(vb_path)[0] + '.ib'
            fmt_path = os.path.splitext(vb_path)[0] + '.fmt'

            # FIXME: ExportHelper will check for overwriting vb_path, but not ib_path

            export_3dmigoto(self, context, vb_path, ib_path, fmt_path)
        except Fatal as e:
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}


class Export3DMigotoGenshin(bpy.types.Operator, ExportHelper):
    """Export a mesh for re-injection into a game with 3DMigoto"""
    bl_idname = "export_mesh_genshin.migoto"
    bl_label = "Export Genshin mod folder"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = '.vb'
    filter_glob : StringProperty(
            default='*.vb',
            options={'HIDDEN'},
            )

    use_foldername : BoolProperty(
        name="Use foldername when exporting",
        description="Sets the export name equal to the foldername you are exporting to. Keep true unless you have changed the names",
        default=True,
    )

    ignore_hidden : BoolProperty(
        name="Ignore hidden objects",
        description="Does not use objects in the Blender window that are hidden while exporting mods",
        default=True,
    )

    only_selected : BoolProperty(
        name="Only export selected",
        description="Uses only the selected objects when deciding which meshes to export",
        default=False,
    )

    no_ramps : BoolProperty(
        name="Ignore shadow ramps/metal maps/diffuse guide",
        description="Skips exporting shadow ramps, metal maps and diffuse guides",
        default=True,
    )

    delete_intermediate : BoolProperty(
        name="Delete intermediate files",
        description="Deletes the intermediate vb/ib files after a successful export to reduce clutter",
        default=True,
    )

    credit : StringProperty(
        name="Credit",
        description="Name that pops up on screen when mod is loaded. If left blank, will result in no pop up",
        default='',
    )
    
    outline_optimization : BoolProperty(
        name="Outline Optimization",
        description="Recalculate outlines. Recommended for final export. Check more options below to improve quality",
        default=False,
    )
    
    toggle_rounding_outline : BoolProperty(
        name="Round vertex positions",
        description="Rounding of vertex positions to specify which are the overlapping vertices",
        default=True,
    ) 
    
    decimal_rounding_outline : bpy.props.IntProperty(
        name="Decimals:",
        description="Rounding of vertex positions to specify which are the overlapping vertices",
        default=3,
    )

    angle_weighted : BoolProperty(
        name="Weight by angle",
        description="Optional: calculate angles to improve accuracy of outlines. Slow",
        default=False,
    )

    overlapping_faces : BoolProperty(
        name="Ignore overlapping faces",
        description="Detect and ignore overlapping/antiparallel faces to avoid buggy outlines",
        default=False,
    )

    detect_edges : BoolProperty(
        name="Calculate edges",
        description="Calculate for disconnected edges when rounding, closing holes in the edge outline",
        default=False,
    )

    calculate_all_faces : BoolProperty(
        name="Calculate outline for all faces",
        description="Calculate outline for all faces, which is especially useful if you have any flat shaded non-edge faces. Slow",
        default=False,
    )

    nearest_edge_distance : bpy.props.FloatProperty(
        name="Distance:",
        description="Expand grouping for edge vertices within this radial distance to close holes in the edge outline. Requires rounding",
        default=0.001,
        soft_min=0,
    )
    
    def draw(self, context):
        layout = self.layout
        col = layout.column(align=True)
        
        col.prop(self, 'use_foldername')
        col.prop(self, 'ignore_hidden')
        col.prop(self, 'only_selected')
        col.prop(self, 'no_ramps')
        col.prop(self, 'delete_intermediate')
        col.prop(self, 'credit')
        layout.separator()
        
        col = layout.column(align=True)
        col.prop(self, 'outline_optimization')
        
        if self.outline_optimization:
            col.prop(self, 'toggle_rounding_outline', text='Vertex Position Rounding', toggle=True, icon="SHADING_WIRE")
            col.prop(self, 'decimal_rounding_outline')
            if self.toggle_rounding_outline:
                col.prop(self, 'detect_edges')
            if self.detect_edges and self.toggle_rounding_outline:
                col.prop(self, 'nearest_edge_distance')
            col.prop(self, 'overlapping_faces')
            col.prop(self, 'angle_weighted')
            col.prop(self, 'calculate_all_faces')

    def execute(self, context):
        try:
            vb_path = self.filepath
            ib_path = os.path.splitext(vb_path)[0] + '.ib'
            fmt_path = os.path.splitext(vb_path)[0] + '.fmt'
            object_name = os.path.splitext(os.path.basename(self.filepath))[0]

            # FIXME: ExportHelper will check for overwriting vb_path, but not ib_path
            Outline_Properties = (self.outline_optimization, self.toggle_rounding_outline, self.decimal_rounding_outline, self.angle_weighted, self.overlapping_faces, self.detect_edges, self.calculate_all_faces, self.nearest_edge_distance)
            export_3dmigoto_genshin(self, context, object_name, vb_path, ib_path, fmt_path, self.use_foldername, self.ignore_hidden, self.only_selected, self.no_ramps, self.delete_intermediate, self.credit, Outline_Properties)
        except Fatal as e:
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}


def apply_vgmap(operator, context, targets=None, filepath='', commit=False, reverse=False, suffix='', rename=False, cleanup=False):
    if not targets:
        targets = context.selected_objects

    if not targets:
        raise Fatal('No object selected')

    vgmap = json.load(open(filepath, 'r'))

    if reverse:
        vgmap = {int(v):int(k) for k,v in vgmap.items()}
    else:
        vgmap = {k:int(v) for k,v in vgmap.items()}

    for obj in targets:
        if commit:
            raise Fatal('commit not yet implemented')

        prop_name = '3DMigoto:VGMap:' + suffix
        obj[prop_name] = keys_to_strings(vgmap)

        if rename:
            for k,v in vgmap.items():
                if str(k) in obj.vertex_groups.keys():
                    continue
                if str(v) in obj.vertex_groups.keys():
                    obj.vertex_groups[str(v)].name = k
                else:
                    obj.vertex_groups.new(name=str(k))
        if cleanup:
            for vg in obj.vertex_groups:
                if vg.name not in vgmap:
                    obj.vertex_groups.remove(vg)

        if '3DMigoto:VBLayout' not in obj:
            operator.report({'WARNING'}, '%s is not a 3DMigoto mesh. Vertex Group Map custom property applied anyway' % obj.name)
        else:
            operator.report({'INFO'}, 'Applied vgmap to %s' % obj.name)

def update_vgmap(operator, context, vg_step=1):
    if not context.selected_objects:
        raise Fatal('No object selected')

    for obj in context.selected_objects:
        vgmaps = {k:keys_to_ints(v) for k,v in obj.items() if k.startswith('3DMigoto:VGMap:')}
        if not vgmaps:
            raise Fatal('Selected object has no 3DMigoto vertex group maps')
        for (suffix, vgmap) in vgmaps.items():
            highest = max(vgmap.values())
            for vg in obj.vertex_groups.keys():
                if vg.isdecimal():
                    continue
                if vg in vgmap:
                    continue
                highest += vg_step
                vgmap[vg] = highest
                operator.report({'INFO'}, 'Assigned named vertex group %s = %i' % (vg, vgmap[vg]))
            obj[suffix] = vgmap

class ApplyVGMap(bpy.types.Operator, ImportHelper):
    """Apply vertex group map to the selected object"""
    bl_idname = "mesh.migoto_vertex_group_map"
    bl_label = "Apply 3DMigoto vgmap"
    bl_options = {'UNDO'}

    filename_ext = '.vgmap'
    filter_glob : StringProperty(
            default='*.vgmap',
            options={'HIDDEN'},
            )

    #commit : BoolProperty(
    #        name="Commit to current mesh",
    #        description="Directly alters the vertex groups of the current mesh, rather than performing the mapping at export time",
    #        default=False,
    #        )

    rename : BoolProperty(
            name="Rename existing vertex groups",
            description="Rename existing vertex groups to match the vgmap file",
            default=True,
            )

    cleanup : BoolProperty(
            name="Remove non-listed vertex groups",
            description="Remove any existing vertex groups that are not listed in the vgmap file",
            default=False,
            )

    reverse : BoolProperty(
            name="Swap from & to",
            description="Switch the order of the vertex group map - if this mesh is the 'to' and you want to use the bones in the 'from'",
            default=False,
            )

    suffix : StringProperty(
            name="Suffix",
            description="Suffix to add to the vertex buffer filename when exporting, for bulk exports of a single mesh with multiple distinct vertex group maps",
            default='',
            )

    def invoke(self, context, event):
        self.suffix = ''
        return ImportHelper.invoke(self, context, event)

    def execute(self, context):
        try:
            keywords = self.as_keywords(ignore=('filter_glob',))
            apply_vgmap(self, context, **keywords)
        except Fatal as e:
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}

class UpdateVGMap(bpy.types.Operator):
    """Assign new 3DMigoto vertex groups"""
    bl_idname = "mesh.update_migoto_vertex_group_map"
    bl_label = "Assign new 3DMigoto vertex groups"
    bl_options = {'UNDO'}

    vg_step : bpy.props.IntProperty(
            name="Vertex group step",
            description='If used vertex groups are 0,1,2,3,etc specify 1. If they are 0,3,6,9,12,etc specify 3',
            default=1,
            min=1,
            )

    def invoke(self, context, event):
        wm = context.window_manager
        return wm.invoke_props_dialog(self)

    def execute(self, context):
        try:
            keywords = self.as_keywords()
            update_vgmap(self, context, **keywords)
        except Fatal as e:
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}

class ConstantBuffer(object):
    def __init__(self, f, start_idx, end_idx):
        self.entries = []
        entry = []
        i = 0
        for line in map(str.strip, f):
            if line.startswith('buf') or line.startswith('cb'):
                entry.append(float(line.split()[1]))
                if len(entry) == 4:
                    if i >= start_idx:
                        self.entries.append(entry)
                    else:
                        print('Skipping', entry)
                    entry = []
                    i += 1
                    if end_idx and i > end_idx:
                        break
        assert(entry == [])

    def as_3x4_matrices(self):
        return [ Matrix(self.entries[i:i+3]) for i in range(0, len(self.entries), 3) ]

def import_pose(operator, context, filepath=None, limit_bones_to_vertex_groups=True, axis_forward='-Z', axis_up='Y', pose_cb_off=[0,0], pose_cb_step=1):
    pose_buffer = ConstantBuffer(open(filepath, 'r'), *pose_cb_off)

    matrices = pose_buffer.as_3x4_matrices()

    obj = context.object
    if not context.selected_objects:
        obj = None

    if limit_bones_to_vertex_groups and obj:
        matrices = matrices[:len(obj.vertex_groups)]

    name = os.path.basename(filepath)
    arm_data = bpy.data.armatures.new(name)
    arm = bpy.data.objects.new(name, object_data=arm_data)

    conversion_matrix = axis_conversion(from_forward=axis_forward, from_up=axis_up).to_4x4()

    link_object_to_scene(context, arm)

    # Construct bones (FIXME: Position these better)
    # Must be in edit mode to add new bones
    select_set(arm, True)
    set_active_object(context, arm)
    bpy.ops.object.mode_set(mode='EDIT')
    for i, matrix in enumerate(matrices):
        bone = arm_data.edit_bones.new(str(i * pose_cb_step))
        bone.tail = Vector((0.0, 0.10, 0.0))
    bpy.ops.object.mode_set(mode='OBJECT')

    # Set pose:
    for i, matrix in enumerate(matrices):
        bone = arm.pose.bones[str(i * pose_cb_step)]
        matrix.resize_4x4()
        bone.matrix_basis = matmul(matmul(conversion_matrix, matrix), conversion_matrix.inverted())

    # Apply pose to selected object, if any:
    if obj is not None:
        mod = obj.modifiers.new(arm.name, 'ARMATURE')
        mod.object = arm
        obj.parent = arm
        # Hide pose object if it was applied to another object:
        hide_set(arm, True)

@orientation_helper(axis_forward='-Z', axis_up='Y')
class Import3DMigotoPose(bpy.types.Operator, ImportHelper, IOOBJOrientationHelper):
    """Import a pose from a 3DMigoto constant buffer dump"""
    bl_idname = "armature.migoto_pose"
    bl_label = "Import 3DMigoto Pose"
    bl_options = {'UNDO'}

    filename_ext = '.txt'
    filter_glob : StringProperty(
            default='*.txt',
            options={'HIDDEN'},
            )

    limit_bones_to_vertex_groups : BoolProperty(
            name="Limit Bones to Vertex Groups",
            description="Limits the maximum number of bones imported to the number of vertex groups of the active object",
            default=True,
            )

    pose_cb_off : bpy.props.IntVectorProperty(
            name="Bone CB range",
            description='Indicate start and end offsets (in multiples of 4 component values) to find the matrices in the Bone CB',
            default=[0,0],
            size=2,
            min=0,
            )

    pose_cb_step : bpy.props.IntProperty(
            name="Vertex group step",
            description='If used vertex groups are 0,1,2,3,etc specify 1. If they are 0,3,6,9,12,etc specify 3',
            default=1,
            min=1,
            )

    def execute(self, context):
        try:
            keywords = self.as_keywords(ignore=('filter_glob',))
            import_pose(self, context, **keywords)
        except Fatal as e:
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}

def find_armature(obj):
    if obj is None:
        return None
    if obj.type == 'ARMATURE':
        return obj
    return obj.find_armature()

def copy_bone_to_target_skeleton(context, target_arm, new_name, src_bone):
    is_hidden = hide_get(target_arm)
    is_selected = select_get(target_arm)
    prev_active = get_active_object(context)
    hide_set(target_arm, False)
    select_set(target_arm, True)
    set_active_object(context, target_arm)

    bpy.ops.object.mode_set(mode='EDIT')
    bone = target_arm.data.edit_bones.new(new_name)
    bone.tail = Vector((0.0, 0.10, 0.0))
    bpy.ops.object.mode_set(mode='OBJECT')

    bone = target_arm.pose.bones[new_name]
    bone.matrix_basis = src_bone.matrix_basis

    set_active_object(context, prev_active)
    select_set(target_arm, is_selected)
    hide_set(target_arm, is_hidden)

def merge_armatures(operator, context):
    target_arm = find_armature(context.object)
    if target_arm is None:
        raise Fatal('No active target armature')
    #print('target:', target_arm)

    for src_obj in context.selected_objects:
        src_arm = find_armature(src_obj)
        if src_arm is None or src_arm == target_arm:
            continue
        #print('src:', src_arm)

        # Create mapping between common bones:
        bone_map = {}
        for src_bone in src_arm.pose.bones:
            for dst_bone in target_arm.pose.bones:
                # Seems important to use matrix_basis - if using 'matrix'
                # and merging multiple objects together, the last inserted bone
                # still has the identity matrix when merging the next pose in
                if src_bone.matrix_basis == dst_bone.matrix_basis:
                    if src_bone.name in bone_map:
                        operator.report({'WARNING'}, 'Source bone %s.%s matched multiple bones in the destination: %s, %s' %
                                (src_arm.name, src_bone.name, bone_map[src_bone.name], dst_bone.name))
                    else:
                        bone_map[src_bone.name] = dst_bone.name

        # Can't have a duplicate name, even temporarily, so rename all the
        # vertex groups first, and rename the source pose bones to match:
        orig_names = {}
        for vg in src_obj.vertex_groups:
            orig_name = vg.name
            vg.name = '%s.%s' % (src_arm.name, vg.name)
            orig_names[vg.name] = orig_name

        # Reassign vertex groups to matching bones in target armature:
        for vg in src_obj.vertex_groups:
            orig_name = orig_names[vg.name]
            if orig_name in bone_map:
                print('%s.%s -> %s' % (src_arm.name, orig_name, bone_map[orig_name]))
                vg.name = bone_map[orig_name]
            elif orig_name in src_arm.pose.bones:
                # FIXME: Make optional
                print('%s.%s -> new %s' % (src_arm.name, orig_name, vg.name))
                copy_bone_to_target_skeleton(context, target_arm, vg.name, src_arm.pose.bones[orig_name])
            else:
                print('Vertex group %s missing corresponding bone in %s' % (orig_name, src_arm.name))

        # Change existing armature modifier to target:
        for modifier in src_obj.modifiers:
            if modifier.type == 'ARMATURE' and modifier.object == src_arm:
                modifier.object = target_arm
        src_obj.parent = target_arm
        unlink_object(context, src_arm)

class Merge3DMigotoPose(bpy.types.Operator):
    """Merge identically posed bones of related armatures into one"""
    bl_idname = "armature.merge_pose"
    bl_label = "Merge 3DMigoto Poses"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            merge_armatures(self, context)
        except Fatal as e:
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}

class DeleteNonNumericVertexGroups(bpy.types.Operator):
    """Remove vertex groups with non-numeric names"""
    bl_idname = "vertex_groups.delete_non_numeric"
    bl_label = "Remove non-numeric vertex groups"
    bl_options = {'UNDO'}

    def execute(self, context):
        try:
            for obj in context.selected_objects:
                for vg in reversed(obj.vertex_groups):
                    if vg.name.isdecimal():
                        continue
                    print('Removing vertex group', vg.name)
                    obj.vertex_groups.remove(vg)
        except Fatal as e:
            self.report({'ERROR'}, str(e))
        return {'FINISHED'}

def menu_func_import_fa(self, context):
    self.layout.operator(Import3DMigotoFrameAnalysis.bl_idname, text="3DMigoto frame analysis dump (vb.txt + ib.txt)")

def menu_func_import_raw(self, context):
    self.layout.operator(Import3DMigotoRaw.bl_idname, text="3DMigoto raw buffers (.vb + .ib)")

def menu_func_import_pose(self, context):
    self.layout.operator(Import3DMigotoPose.bl_idname, text="3DMigoto pose (.txt)")

def menu_func_export(self, context):
    self.layout.operator(Export3DMigoto.bl_idname, text="3DMigoto raw buffers (.vb + .ib)")

def menu_func_export_genshin(self, context):
    self.layout.operator(Export3DMigotoGenshin.bl_idname, text="Exports Genshin Mod Folder")

def menu_func_apply_vgmap(self, context):
    self.layout.operator(ApplyVGMap.bl_idname, text="Apply 3DMigoto vertex group map to current object (.vgmap)")

register_classes = (
    Import3DMigotoFrameAnalysis,
    Import3DMigotoRaw,
    Import3DMigotoReferenceInputFormat,
    Export3DMigoto,
    Export3DMigotoGenshin,
    ApplyVGMap,
    UpdateVGMap,
    Import3DMigotoPose,
    Merge3DMigotoPose,
    DeleteNonNumericVertexGroups,
)

def register():
    for cls in register_classes:
        make_annotations(cls)
        bpy.utils.register_class(cls)

    import_menu.append(menu_func_import_fa)
    import_menu.append(menu_func_import_raw)
    export_menu.append(menu_func_export)
    export_menu.append(menu_func_export_genshin)
    import_menu.append(menu_func_apply_vgmap)
    import_menu.append(menu_func_import_pose)

def unregister():
    for cls in reversed(register_classes):
        bpy.utils.unregister_class(cls)

    import_menu.remove(menu_func_import_fa)
    import_menu.remove(menu_func_import_raw)
    export_menu.remove(menu_func_export)
    export_menu.remove(menu_func_export_genshin)
    import_menu.remove(menu_func_apply_vgmap)
    import_menu.remove(menu_func_import_pose)

if __name__ == "__main__":
    register()
