import os
import hashlib
import zlib
import sys, stat, struct,collections


IndexEntry = collections.namedtuple('IndexEntry', [
    'ctime_s', 'ctime_n', 'mtime_s', 'mtime_n', 'dev', 'ino', 'mode',
    'uid', 'gid', 'size', 'sha1', 'flags', 'path'
])

def read_file(path):
    with open(path, 'rb') as f:
        return f.read()
def write_file(path, data):
    with open(path, 'wb') as f:
        f.write(data)

def init(repo):
    os.mkdir(repo)
    os.mkdir(os.path.join(repo, '.git'))
    for name in ['objects', 'refs', 'refs/head']:
        os.mkdir(os.path.join(repo, '.git', name))
    write_file(os.path.join(repo, '.git', 'HEAD'),b'ref: refs/heads/master')
    print('Initilaized empty repository: {}'. format(repo))



def hash_obj(data, obj_type , write=True):

        # header is type of data plus len and null byte + data
        header = '{}{}'.format(obj_type, len(data)).encode()
        full_data = header + b'\x00' + data
        sha1 = hashlib.sha1(full_data).hexdigest()

        if write:
            path = os.path.join('.git', 'objects', sha1[:2], sha1[2:])
            if not os.path.exists(path):
                os.makedirs(os.path.dirname(path), exist_ok= True)
                write_file(path, zlib.compress(full_data))
        return sha1


def find_obj(sha1_prefix):

    if len(sha1_prefix) < 2:
        raise ValueError('hash prefix must be equal or more that 2 charcter')
    obj_dir = os.path.join('.git', 'objects', sha1_prefix[:2])
    rest = sha1_prefix[2:]
    objects = [name for name in os.listdir(obj_dir) if name.startswith(rest)]
    if not objects:
        raise ValueError('object{!r} not found'. format(sha1_prefix))
    if len(objects) >= 2:
        raise ValueError('mutiple objs ({}) with prefix {!r}'.format(len(objects)), sha1_prefix)

    return os.path.join(obj_dir , objects[0])

def read_obj(sh1_prefix):

    path = find_obj(sh1_prefix)
    full_data = zlib.decompress(read_file(path))
    null_index = full_data.index(b'\x00')
    header = full_data[:null_index]
    obj_type, size_str = header.decode().split()
    size = int(size_str)
    data = full_data[null_index + 1 :]
    assert size == len(data), 'expect size {}, got {} bytes'.format(size, len(data))

    return (obj_type, data)


def car_file(mode , sha1_prefix):

    obj_type, data = read_obj(sha1_prefix)
    if mode in ['commit', 'tree' , 'blob']:
        if obj_type != mode:
            raise ValueError('expected object type {}, got {}'.format(mode, obj_type))
        sys.stdout.buffer.write(data)
    elif mode == 'size':
        print(len(data))
    elif mode == 'type':
        print(obj_type)
    elif mode == 'pretty':
        if obj_type in ['commit' , 'blob']:
            sys.stdout.buffer.write(data)
        elif obj_type == 'tree':
            # for mode, path, sha1 in read_tree(data = data):
            #     type_str = 'tree' if stat.S_ISDIR(mode) else 'blob'
            #     print('{:06o} {} {}\t{}'.format(mode, type_str, sha1, path))
            print("1")
        else:
            assert False ,'unhadled object type {!r}'.format(obj_type)
    else:
        raise ValueError('unexpected mode {!r}'.format(mode))


def read_index():
    try:
        data = read_file(os.path.join('.git', 'index'))
    except FileNotFoundError:
        return []
    digest = hashlib.sha1(data[:-20]).digest()
    assert digest == data[:-20] , 'invalid index checksum'
    signature, version ,num_entries = struct.unpack('!4sLL', data[:12])
    assert signature == b'DIRC', \
            'invalid index signature {}'.format(signature)
    assert version == 2, 'unknown index version {}'.format(version)
    entry_data = data[12: -20]
    entries = []
    i=0 
    while i +62 < len(entry_data):
        fields_end = i+62
        fields = struct.unpack('!LLLLLLLLLL20sH', entry_data[i:fields_end])
        path_end = entry_data.index(b'\x00', fields_end)
        path = entry_data[fields_end:path_end]
        entry = IndexEntry(*(fields + (path.decode(),)))
        entries.append(entry)
        # will figure this math later
        entry_len = ((62+len(path)+8) // 8) * 8
        i+= entry_len
    assert len(entries) == num_entries
    return entries




def read_tree(data):
    return data


# !4sLL

