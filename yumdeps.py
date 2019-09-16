import re

STATE_START = 0
STATE_PACKAGE = 1
STATE_DEPENDENCY = 2
STATE_PROVIDER = 3

KEY_PACKAGE = 'package:'
KEY_DEPENDENCY = 'dependency:'
KEY_PROVIDER = 'provider:'
KEY_LIST = [KEY_PACKAGE, KEY_DEPENDENCY, KEY_PROVIDER]

UNKNOWN_ARCH = 'Unknown'
UNKNOWN_REPO = 'Unknown'


# class DepList:
#
#     def __init__(self):
#         self.pkg = {}
#         self.dep = {}
#
#     @staticmethod
#     def _extract_name_and_arch(pkg_name):
#         try:
#             name, arch = pkg_name.split('.')
#         except ValueError:
#             name = pkg_name
#             arch = UNKNOWN_ARCH
#         return name, arch
#
#     @staticmethod
#     def _extract_arch(pkg_name):
#         try:
#             _, arch = pkg_name.split('.')
#         except ValueError:
#             arch = UNKNOWN_ARCH
#         return arch
#
#     @staticmethod
#     def _extract_version_and_repo(pkg_version):
#         try:
#             version, repo = pkg_version.split('.')
#         except ValueError:
#             version = pkg_version
#             repo = UNKNOWN_REPO
#         return version, repo
#
#     @staticmethod
#     def _extract_repo(pkg_version):
#         try:
#             _, repo = pkg_version.split('.')
#         except ValueError:
#             repo = UNKNOWN_REPO
#         return repo
#
#     def add_package(self, pkg_name, pkg_version):
#
#         # p_name, p_arch = DepList._name_and_arch(pkg_name)
#         # p_version, p_repo = DepList._version_and_repo(pkg_name)
#         # p_arch = DepList._extract_arch(pkg_name)
#         # p_version, p_repo = DepList._extract_version_and_repo(pkg_version)
#         print 'add_package', pkg_name, pkg_version
#         if pkg_name not in self.pkg:
#             self.pkg[pkg_name] = pkg_version
#             self.dep[pkg_name] = {}
#         else:
#             print 'package ' + pkg_name + ' already exists, ignored'
#
#     def add_dependency(self, pkg_name, dep_name):
#         p_name, _ = DepList._extract_name_and_arch(pkg_name)
#         if p_name in self.dep:
#             if dep_name not in self.dep[p_name]:
#                 self.dep[p_name].update({dep_name: []})
#             else:
#                 raise ValueError('dependency ' + dep_name + ' already exists')
#         else:
#             raise ValueError('package ' + pkg_name + ' does not exist')
#
#     def add_provider(self, pkg_name, dep_name, provider, version):
#         p_name, _ = DepList._extract_name_and_arch(pkg_name)
#         if p_name in self.dep:
#             if dep_name in self.dep[p_name]:
#                 r_name, r_repo = DepList._extract_version_and_repo(version)
#                 self.dep[p_name][dep_name].append((r_name, r_repo))
#                 print 'adding provider', provider
#             else:
#                 raise ValueError('package ' + pkg_name + ' does not exist')
#         else:
#             raise ValueError('package ' + pkg_name + 'does not exist')
#
#     def dump(self):
#         for pkg_name in self.pkg:
#             print 'Package', pkg_name
#             for dep_name in self.pkg[pkg_name]:
#                 print '  Dependency'


class PkgDict:

    def __init__(self):
        self.pkg = {}

    def add_package(self, pkg_name, pkg_version):
        print 'add_package', pkg_name, pkg_version
        if pkg_name not in self.pkg:
            self.pkg[pkg_name] = pkg_version
        else:
            print 'package ' + pkg_name + ' already exists, ignored'

    def is_package(self, pkg_name):
        return pkg_name in self.pkg


class DepDict:

    def __init__(self):
        self.dep = {}

    def add_dependency(self, pkg_name, dep_name):
        print 'add_dependency', pkg_name, dep_name
        if pkg_name in self.dep:
            if dep_name not in self.dep[pkg_name]:
                self.dep[pkg_name].update({dep_name: []})
            else:
                print 'dependency ' + dep_name + ' already exists for package ' + pkg_name
        else:
            self.dep[pkg_name] = {dep_name: []}

    def add_provider(self, pkg_name, dep_name, provider, version):
        # arch, _ = DepDict._extract_name_and_arch(pkg_name)
        if pkg_name in self.dep:
            if dep_name in self.dep[pkg_name]:
                # r_name, r_repo = DepDict._extract_version_and_repo(version)
                self.dep[pkg_name][dep_name].append(provider)
                print 'adding provider', provider
            else:
                raise ValueError('package ' + pkg_name + ' does not exist')
        else:
            raise ValueError('package ' + pkg_name + 'does not exist')

    def dump(self):
        for pkg_name in sorted(self.dep):
            print 'Package', pkg_name
            for dep_name in sorted(self.dep[pkg_name]):
                print ' ' * 2 + dep_name
                for name in sorted(self.dep[pkg_name][dep_name]):
                    print ' ' * 4, name


def split_line(line):
    words = line.split()
    key = words[0]
    if key in KEY_LIST:
        if key == KEY_PACKAGE:
            return key, words[1], words[2]
        elif key == KEY_DEPENDENCY:
            return key, words[1], None
        elif key == KEY_PROVIDER:
            return key, words[1], words[2]
    else:
        return None, None, None


def parse_file(file_name):

    try:
        f = open(file_name, 'r')
    except IOError as e:
        print e
        return

    pkg_dict = parse_file_pass1(f)
    f.seek(0)
    dep_dict = parse_file_pass2(f)
    dep_dict.dump()


def parse_file_pass1(f):
    pkg = PkgDict()
    for line in f:
        key, name, version = split_line(line)
        if key == KEY_PACKAGE:
            pkg.add_package(name, version)
    return pkg


def parse_file_pass2(f):

    dep = DepDict()
    pkg_name = 'undefined'
    dep_name = 'undefined'

    for line in f:

        key, name, version = split_line(line)

        if key == KEY_PACKAGE:
            print '\nfound package', name, version
            pkg_name = name
        elif key == KEY_DEPENDENCY:
            print '  found dependency', name
            dep_name = name
            dep.add_dependency(pkg_name, dep_name)
        elif key == KEY_PROVIDER:
            print '    found provider', pkg_name, dep_name, name, version
            dep.add_provider(pkg_name, dep_name, name, version)

    return dep

# def parse_deplist(file_name):
#
#     deplist = DepList()
#
#     try:
#         f = open(file_name, 'r')
#     except IOError as e:
#         print e
#         return
#
#     state = STATE_PACKAGE
#     pkg_name = ''
#     dep_name = ''
#
#     for line in f:
#
#         key, name, version = split_line(line)
#         if key is None:
#             continue
#         # print key, name, version
#
#         if state == STATE_PACKAGE:
#             if key == KEY_PACKAGE:
#                 print '\nfound package', name, version
#                 pkg_name = name
#                 deplist.add_package(name, version)
#                 state = STATE_DEPENDENCY
#         elif state == STATE_DEPENDENCY:
#             if key == KEY_DEPENDENCY:
#                 print '  found dependency', name
#                 dep_name = name
#                 # deplist.add_dependency(pkg_name, name)
#                 state = STATE_PROVIDER
#
#         elif state == STATE_PROVIDER:
#             if key == KEY_PROVIDER:
#                 # deplist.add_provider(pkg_name, dep_name, provider, version)
#                 print '    found provider', name, version
#             elif key == KEY_PACKAGE:
#                 print '\nfound package', name, version
#                 deplist.add_package(name, version)
#                 pkg_name = name
#                 state = STATE_DEPENDENCY
#             elif key == KEY_DEPENDENCY:
#                 print '  found dependency', name
#                 state = STATE_PROVIDER
#
#         else:
#             print state
#             break

if __name__ == '__main__':
    parse_file('deplist')