import logging

KEY_PACKAGE = 'package:'
KEY_DEPENDENCY = 'dependency:'
KEY_PROVIDER = 'provider:'
KEY_DEP_LIST = [KEY_PACKAGE, KEY_DEPENDENCY, KEY_PROVIDER]

KEY_NAME = 'Name'
KEY_ARCH = 'Arch'
KEY_VERSION = 'Version'
KEY_RELEASE = 'Release'
KEY_REPOSITORY = 'Repo'
KEY_INFO_LIST = [KEY_NAME, KEY_ARCH, KEY_VERSION, KEY_RELEASE, KEY_REPOSITORY]

# debug = True
LOG_INFO = 1
LOG_WARNING = 2


# class PkgDict:
#
#     def __init__(self):
#         self.pkg = {}
#
#     def add_package(self, pkg_name, pkg_version):
#         print 'add_package', pkg_name, pkg_version
#         if pkg_name not in self.pkg:
#             self.pkg[pkg_name] = pkg_version
#         else:
#             print 'package ' + pkg_name + ' already exists, ignored'
#
#     def is_package(self, pkg_name):
#         return pkg_name in self.pkg
#
#
# class DepDict:
#
#     def __init__(self):
#         self.dep = {}
#
#     def add_dependency(self, pkg_name, dep_name):
#         print 'add_dependency', pkg_name, dep_name
#         if pkg_name in self.dep:
#             if dep_name not in self.dep[pkg_name]:
#                 self.dep[pkg_name].update({dep_name: []})
#             else:
#                 print 'dependency ' + dep_name + ' already exists for package ' + pkg_name
#         else:
#             self.dep[pkg_name] = {dep_name: []}
#
#     def add_provider(self, pkg_name, dep_name, provider, version):
#         # arch, _ = DepDict._extract_name_and_arch(pkg_name)
#         if pkg_name in self.dep:
#             if dep_name in self.dep[pkg_name]:
#                 # r_name, r_repo = DepDict._extract_version_and_repo(version)
#                 self.dep[pkg_name][dep_name].append((provider, version))
#                 print 'adding provider', provider
#             else:
#                 raise ValueError('package ' + pkg_name + ' does not exist')
#         else:
#             raise ValueError('package ' + pkg_name + 'does not exist')
#
#     def dump(self):
#         for pkg_name in sorted(self.dep):
#             print 'Package', pkg_name
#             for dep_name in sorted(self.dep[pkg_name]):
#                 print ' ' * 2 + dep_name
#                 for name in sorted(self.dep[pkg_name][dep_name]):
#                     print ' ' * 4, name

class Dep:
    LOG_INFO = 0
    LOG_WARNING = 1

    def __init__(self):
        self.pkg = {}
        self.dep = {}

    # def add_package(self, pkg_name, pkg_version):
    #     logging.debug('add_package ' + pkg_name + ' ' + pkg_version)
    #     if pkg_name not in self.pkg:
    #         self.pkg[pkg_name] = pkg_version
    #         self.dep[pkg_name] = {}
    #     else:
    #         logging.warning('package ' + pkg_name + ' already exists, ignored')

    def add_package(self, pkg_name):
        logging.debug('add_package ' + pkg_name)
        if pkg_name not in self.pkg:
            self.pkg[pkg_name] = {KEY_VERSION: '', KEY_RELEASE: '', KEY_ARCH: '', KEY_REPOSITORY: ''}
            self.dep[pkg_name] = {}
        else:
            logging.warning('package ' + pkg_name + ' already exists, ignored')

    def add_version(self, pkg_name, version):
        logging.debug('add_version ' + pkg_name + ' ' + version)
        if pkg_name in self.pkg:
            self.pkg[pkg_name][KEY_VERSION] = version

    def add_release(self, pkg_name, release):
        logging.debug('add_release ' + pkg_name + ' ' + release)
        if pkg_name in self.pkg:
            self.pkg[pkg_name][KEY_RELEASE] = release

    def add_arch(self, pkg_name, arch):
        logging.debug('add_arch ' + pkg_name + ' ' + arch)
        if pkg_name in self.pkg:
            self.pkg[pkg_name][KEY_ARCH] = arch

    def add_repository(self, pkg_name, repository):
        logging.debug('add_repository ' + pkg_name + ' ' + repository)
        if pkg_name in self.pkg:
            self.pkg[pkg_name][KEY_REPOSITORY] = repository

    def add_dependency(self, pkg_name, dep_name):
        logging.debug('add_dependency ' + pkg_name + ' ' + dep_name)
        if pkg_name in self.dep:
            if dep_name not in self.dep[pkg_name]:
                self.dep[pkg_name].update({dep_name: []})
            else:
                logging.warning('dependency ' + dep_name + ' already exists for package ' + pkg_name)
        else:
            self.dep[pkg_name] = {dep_name: []}

    def add_provider(self, pkg_name, dep_name, provider, version):
        # arch, _ = DepDict._extract_name_and_arch(pkg_name)
        if pkg_name in self.dep:
            if dep_name in self.dep[pkg_name]:
                # r_name, r_repo = DepDict._extract_version_and_repo(version)
                self.dep[pkg_name][dep_name].append((provider, version))
                logging.debug('adding provider ' + provider)
            else:
                raise ValueError('dependency ' + dep_name + ' for package ' + pkg_name + ' does not exist')
        else:
            raise ValueError('package ' + pkg_name + 'does not exist')

    def get_version(self, pkg_name):
        if pkg_name in self.pkg:
            return self.pkg[pkg_name][KEY_VERSION]
        else:
            return 'undefined-version'

    def get_release(self, pkg_name):
        if pkg_name in self.pkg:
            return self.pkg[pkg_name][KEY_RELEASE]
        else:
            return 'undefined-release'

    def get_arch(self, pkg_name):
        if pkg_name in self.pkg:
            return self.pkg[pkg_name][KEY_ARCH]
        else:
            return 'undefined-arch'

    def get_repository(self, pkg_name):
        if pkg_name in self.pkg:
            return self.pkg[pkg_name][KEY_REPOSITORY]
        else:
            return 'undefined-repo'

    def get_dependency_names(self, pkg_name):
        if pkg_name in self.dep:
            return sorted(self.dep[pkg_name])
        else:
            logging.debug('no dependencies for package ' + pkg_name)
            return []

    def get_provider_list(self, pkg_name, dep_name):
        if pkg_name in self.dep:
            if dep_name in self.dep[pkg_name]:
                return self.dep[pkg_name][dep_name]
            else:
                raise ValueError('package ' + pkg_name + ' does not exist')
        else:
            raise ValueError('dependency ' + dep_name + ' for package ' + pkg_name + ' does not exist')

    # def exists(self, pkg_name):
    #     return pkg_name in self.pkg

    def dump(self):
        print '\n' + '-' * 80

        for pkg_name in sorted(self.pkg):
            print 'Package {} {} {} {} {}'.format(pkg_name,
                                                  self.get_version(pkg_name),
                                                  self.get_release(pkg_name),
                                                  self.get_arch(pkg_name),
                                                  self.get_repository(pkg_name))
            p_name = pkg_name + '.' + self.get_arch()
            dep_list = self.get_dependency_names(pkg_name)
            for dep_name in self.get_dependency_names(pkg_name):
                print ' ' * 2, dep_name
            #     print ' ' * 2 + dep_name
            # for name, version in sorted(self.dep[pkg_name][dep_name]):
            #     print ' ' * 4, name # + (' yes' if self.exists(name) else ' no')


def split_info_line(line):
    words = line.split(':')
    key = words[0].strip()
    if key in KEY_INFO_LIST:
        return key, words[1].strip()
    else:
        return None, None


def split_dep_line(line):
    words = line.split()
    key = words[0].strip()
    if key == KEY_PACKAGE:
        return key, words[1].strip(), words[2].strip()
    elif key == KEY_DEPENDENCY:
        return key, words[1].strip(), None
    elif key == KEY_PROVIDER:
        return key, words[1].strip(), words[2].strip()
    else:
        return None, None, None


# def parse_file(file_name):
#
#     try:
#         f = open(file_name, 'r')
#     except IOError as e:
#         print e
#         return
#
#     pkg_dict = parse_file_pass1(f)
#     f.seek(0)
#     dep_dict = parse_file_pass2(f)
#     dep_dict.dump()
#
# def parse_file_pass1(f):
#     pkg = PkgDict()
#     for line in f:
#         key, name, version = split_line(line)
#         if key == KEY_PACKAGE:
#             pkg.add_package(name, version)
#     return pkg
#
# def parse_file_pass2(f):
#
#     dep = Dep()
#     pkg_name = 'undefined'
#     dep_name = 'undefined'
#
#     for line in f:
#
#         key, name, version = split_line(line)
#
#         if key == KEY_PACKAGE:
#             print '\nfound package', name, version
#             pkg_name = name
#         elif key == KEY_DEPENDENCY:
#             print '  found dependency', name
#             dep_name = name
#             dep.add_dependency(pkg_name, dep_name)
#         elif key == KEY_PROVIDER:
#             print '    found provider', pkg_name, dep_name, name, version
#             dep.add_provider(pkg_name, dep_name, name, version)
#
#     return dep

# def parse_file(file_name):
#     try:
#         f = open(file_name, 'r')
#     except IOError as e:
#         print e
#         return
#
#     dep = Dep()
#     pkg_name = 'undefined'
#     dep_name = 'undefined'
#
#     for line in f:
#
#         key, name, name = split_dep_line(line)
#
#         if key == KEY_PACKAGE:
#             logging.debug('found package ' + name + ' ' + name)
#             dep.add_package(name, name)
#             pkg_name = name
#         elif key == KEY_DEPENDENCY:
#             logging.debug('  found dependency ' + name)
#             dep.add_dependency(pkg_name, name)
#             dep_name = name
#         elif key == KEY_PROVIDER:
#             logging.debug('    found provider ' + pkg_name + ' ' + dep_name + ' ' + name + ' ' + version)
#             dep.add_provider(pkg_name, dep_name, name, version)
#
#     return dep


def parse_info_file(f, dep):
    """
    :param f:
    :type: file
    :param dep:
    :type: Dep
    :return:
    :rtype: Dep
    """
    pkg_name = 'undefined'

    for line in f:

        key, name = split_info_line(line)
        # print key, name

        if key == KEY_NAME:
            logging.debug('found package ' + name)
            # dep.add_package(name)
            pkg_name = name
            pkg_name = name
        elif key == KEY_VERSION:
            logging.debug('  found version ' + name)
            dep.add_version(pkg_name, name)
        elif key == KEY_RELEASE:
            logging.debug('  found release ' + name)
            dep.add_release(pkg_name, name)
        elif key == KEY_ARCH:
            logging.debug('  found arch ' + name)
            dep.add_arch(pkg_name, name)
        elif key == KEY_REPOSITORY:
            logging.debug('  found repo ' + name)
            dep.add_repository(pkg_name, name)

    return dep


def parse_dep_file(f, dep):
    """
    :param f:
    :type: file
    :param dep:
    :type: Dep
    :return:
    :rtype: Dep
    """
    pkg_name = 'undefined'
    dep_name = 'undefined'

    for line in f:

        key, name, version = split_dep_line(line)

        if key == KEY_PACKAGE:
            logging.debug('found package ' + name + ' ' + name)
            # dep.add_package(name, name)
            pkg_name = name
        elif key == KEY_DEPENDENCY:
            logging.debug('  found dependency ' + name)
            dep.add_dependency(pkg_name, name)
            dep_name = name
        elif key == KEY_PROVIDER:
            logging.debug('    found provider ' + pkg_name + ' ' + dep_name + ' ' + name + ' ' + version)
            dep.add_provider(pkg_name, dep_name, name, version)

    return dep


def parse_files(info_file_name, dep_file_name):

    dep = Dep()

    with open(info_file_name, 'r') as f_info, open(dep_file_name, 'r') as f_dep:
        dep = parse_info_file(f_info, dep)
        dep = parse_dep_file(f_dep, dep)

    print dep.dep['VDCT.i686']
    print dep.get_dependency_names('VDCT.i686')
    dep.dump()


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    # dep = parse_file('pkg.dep')
    # dep.dump()
    parse_files('pkg.info', 'pkg.dep')
