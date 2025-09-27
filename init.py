import os
import hashlib
import zlib

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
