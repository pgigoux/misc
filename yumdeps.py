import logging

# Keywords used to parse the package information file.
# They are also used as indices in the package information dictionary.
KEY_NAME = 'Name'
KEY_ARCH = 'Arch'
KEY_VERSION = 'Version'
KEY_RELEASE = 'Release'
KEY_REPOSITORY = 'Repo'
KEY_SUMMARY = 'Summary'
KEY_INFO_LIST = [KEY_NAME, KEY_ARCH, KEY_VERSION, KEY_RELEASE, KEY_REPOSITORY, KEY_SUMMARY]

# Keywords used to parse the dependency file
KEY_PACKAGE = 'package:'
KEY_DEPENDENCY = 'dependency:'
KEY_PROVIDER = 'provider:'
KEY_DEP_LIST = [KEY_PACKAGE, KEY_DEPENDENCY, KEY_PROVIDER]

# String use to initialize undefined strings
UNDEFINED = 'undefined'


class PkgDep:

    def __init__(self):
        self.pkg = {}
        self.dep = {}

    def add_package(self, pkg_name, arch, version, release, repository, summary):
        """
        Add package information and initialize dependency information.
        If the package already exists, it is overwritten.
        :param pkg_name: package name
        :type pkg_name: str
        :param arch: architecture
        :type arch: str
        :param version: version
        :type version: str
        :param release: release number
        :type release: str
        :param repository: repository providing the package
        :type repository: str
        :param summary: one line description of the package
        :type summary: str
        :return: None
        """
        logging.debug('add_package ' + pkg_name)
        if pkg_name not in self.pkg:
            self.pkg[pkg_name] = {KEY_ARCH: arch, KEY_VERSION: version, KEY_RELEASE: release,
                                  KEY_REPOSITORY: repository, KEY_SUMMARY: summary}
            self.dep[pkg_name] = {}
        else:
            logging.warning('package ' + pkg_name + ' already exists, ignored')

    def add_dependency(self, pkg_name, dep_name):
        """
        Add dependency for a given package.

        :param pkg_name: package name
        :type pkg_name: str
        :param dep_name: dependency name
        :type dep_name: str
        :return: None
        """
        logging.debug('add_dependency ' + pkg_name + ' ' + dep_name)
        if pkg_name in self.dep:
            if dep_name not in self.dep[pkg_name]:
                self.dep[pkg_name].update({dep_name: []})
            else:
                logging.warning('dependency ' + dep_name + ' already exists for package ' + pkg_name)
        else:
            self.dep[pkg_name] = {dep_name: []}

    def add_provider(self, pkg_name, dep_name, provider, version):
        """
        Add provider for a given package and dependency.
        A dependency can be provided by more than one package (e.g. different architectures).
        The provider will be the name of the package that provides the dependency.
        :param pkg_name: package name
        :type pkg_name: str
        :param dep_name: dependency name
        :type dep_name: str
        :param provider: provider name (package)
        :type provider: str
        :param version: provider version
        :type version: str
        :raise ValueError: if package or dependency are nor found.
        ::return: None
        """
        if pkg_name in self.dep:
            if dep_name in self.dep[pkg_name]:
                # r_name, r_repo = DepDict._extract_version_and_repo(version)
                self.dep[pkg_name][dep_name].append((provider, version))
                logging.debug('adding provider ' + provider)
            else:
                raise ValueError('dependency ' + dep_name + ' for package ' + pkg_name + ' does not exist')
        else:
            raise ValueError('package ' + pkg_name + ' does not exist')

    def get_arch(self, pkg_name):
        """
        Return the package architecture.
        The architecture could be UNDEFINED if it was not defined (unlikely).
        :param pkg_name: package name
        :type pkg_name: str
        :raise ValueError: if package is not found
        :return: package architecture
        :rtype: str
        """
        if pkg_name in self.pkg:
            return self.pkg[pkg_name][KEY_ARCH]
        else:
            raise ValueError('package ' + pkg_name + ' does not exist')

    def get_version(self, pkg_name):
        """
        Return the package version (e.g. '2.5.1271')
        :param pkg_name: package name
        :type pkg_name: str
        :raise ValueError: if package is not found
        :return: package version
        :rtype: str
        """
        if pkg_name in self.pkg:
            return self.pkg[pkg_name][KEY_VERSION]
        else:
            raise ValueError('package ' + pkg_name + ' does not exist')

    def get_release(self, pkg_name):
        """
        Return the package release number (e.g. '6', '14.el7.gemini', etc.)
        :param pkg_name: package name
        :type pkg_name: str
        :raise ValueError: if package is not found
        :return: package version
        :rtype: str
        """
        if pkg_name in self.pkg:
            return self.pkg[pkg_name][KEY_RELEASE]
        else:
            raise ValueError('package ' + pkg_name + ' does not exist')

    def get_repository(self, pkg_name):
        """
        Return the package repository (e.g. 'gemini-production/7/x86_64')
        :param pkg_name: package name
        :type pkg_name: str
        :raise ValueError: if package is not found
        :return: package version
        :rtype: str
        """
        if pkg_name in self.pkg:
            return self.pkg[pkg_name][KEY_REPOSITORY]
        else:
            raise ValueError('package ' + pkg_name + ' does not exist')

    def get_summary(self, pkg_name):
        """
        Return the package one line summary.
        :param pkg_name: package name
        :type pkg_name: str
        :raise ValueError: if package is not found
        :return: package version
        :rtype: str
        """
        if pkg_name in self.pkg:
            return self.pkg[pkg_name][KEY_SUMMARY]
        else:
            raise ValueError('package ' + pkg_name + ' does not exist')

    def get_dependency_list(self, pkg_name):
        """
        Return the (sorted) list of dependencies for a given package.
        The list can be empty if the package has no dependencies.
        :param pkg_name: package name
        :type pkg_name: str
        :raise ValueError: if package is not found
        :return: dependency list
        :rtype: list
        """
        if pkg_name in self.dep:
            return sorted(self.dep[pkg_name])
        else:
            raise ValueError('package ' + pkg_name + ' does not exist')

    def get_provider_list(self, pkg_name, dep_name):
        """
        Return the list of providers for a given package and dependency.
        There should be at least one provider for each dependency.
        The providers are returned as a list of tuples; the first element of the tuple is the
        provider name and the second one the provider version
        :param pkg_name: package name
        :type pkg_name: str
        :param dep_name: dependency name
        :type dep_name: str
        :param dep_name:
        :raise ValueError: if package or dependency are not found
        :return: list of providers
        :rtype: list
        """
        if pkg_name in self.dep:
            if dep_name in self.dep[pkg_name]:
                return self.dep[pkg_name][dep_name]
            else:
                raise ValueError('package ' + pkg_name + ' does not exist')
        else:
            raise ValueError('dependency ' + dep_name + ' for package ' + pkg_name + ' does not exist')

    def exists(self, pkg_name):
        """
        Check whether a package exists
        :param pkg_name:
        :return: True if the package is defined, False otherwise
        :rtype: bool
        """
        return pkg_name in self.pkg

    def print_packages_and_dependencies(self):
        """
        Print the package/dependency/provider to the standard output.
        Used for debugging.
        :return:
        """
        print '\n' + '-' * 80
        for pkg_name in sorted(self.pkg):
            print 'Package {} [{}] [{}] [{}] [{}] [{}]'.format(pkg_name,
                                                               self.get_version(pkg_name),
                                                               self.get_release(pkg_name),
                                                               self.get_arch(pkg_name),
                                                               self.get_repository(pkg_name),
                                                               self.get_summary(pkg_name))
            for dep_name in self.get_dependency_list(pkg_name):
                print ' ' * 2 + dep_name
                for p_name, p_version in self.get_provider_list(pkg_name, dep_name):
                    flag = ' yes' if self.exists(p_name) else ' no'
                    print ' ' * 4 + '[' + p_name + ', ' + p_version + ']' + flag


def split_info_line(line):
    """
    Split package info line into (meaningful) words.
    This routine looks for lines containing the package name, architecture, version, release,
    repository and summary information.
    It returns the keyword found and its value, or (None, None) if the line does not contain
    any of the expected keywords.
    :param line: input line
    :type line: str
    :return: tuple with the keyword and value. (None, None) otherwise.
    :rtype: tuple
    """
    words = line.split(':')
    key = words[0].strip()
    if key in KEY_INFO_LIST:
        return key, words[1].strip()
    else:
        return None, None


def split_dep_line(line):
    """
    Split package dependency line into (meaningful) words.
    This routine looks for lines containing package, dependency or provider information.
    It always returns a three element tuple containing the relevant information.
    - Package line: keyword (KEY_PACKAGE), package name and version.
    - Dependency line: keyword (KEY_DEPENDENCY), dependency name and None.
    - Provider: keyword (KEY_PROVIDER), provider name and provider version.
    :param line: input line
    :type line: str
    :return: tuple with relevant information. (None, None, None) otherwise.
    :rtype: tuple
    """
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


def parse_info_file(f, dep):
    """
    Parse a file containing package information.
    This file is generated by another program that runs 'yum info' over a list of packages.
    The package information is scattered in several lines. This function assumes that the
    package name will always come first.
    :param f: info file
    :type f: file
    :param dep: package/dependency object
    :type dep: PkgDep
    :return: updated package/dependency object
    :rtype: PkgDep
    """

    # Initialize values. Only the package name needs to be initialized at this
    # point, but initializing all variables keeps PyCharm happy :)
    pkg_name = UNDEFINED
    pkg_arch = UNDEFINED
    pkg_version = UNDEFINED
    pkg_release = UNDEFINED
    pkg_repository = UNDEFINED
    pkg_summary = UNDEFINED

    for line in f:

        key, name = split_info_line(line)
        # print key, name

        if key == KEY_NAME:
            logging.debug('found package ' + name)

            # Add "previous" package information.
            # The package name will be UNDEFINED the first time.
            if pkg_name != UNDEFINED:
                dep.add_package(pkg_name + '.' + pkg_arch, pkg_arch, pkg_version,
                                pkg_release, pkg_repository, pkg_summary)
            pkg_name = name

            # Reset values
            pkg_arch = UNDEFINED
            pkg_version = UNDEFINED
            pkg_release = UNDEFINED
            pkg_repository = UNDEFINED
            pkg_summary = UNDEFINED

        elif key == KEY_VERSION:
            logging.debug('  found version ' + name)
            pkg_version = name
        elif key == KEY_RELEASE:
            logging.debug('  found release ' + name)
            pkg_release = name
        elif key == KEY_ARCH:
            logging.debug('  found arch ' + name)
            pkg_arch = name
        elif key == KEY_REPOSITORY:
            logging.debug('  found repo ' + name)
            pkg_repository = name
        elif key == KEY_SUMMARY:
            logging.debug('  found summary ' + name)
            pkg_summary = name

    return dep


def parse_dep_file(f, dep):
    """
    Parse dependency file for package, dependency or provider definitions.
    This file is generated by another program that runs 'yum deplist' over a list of packages.
    This function assumes that the package name will always come first.
    :param f: dependency file
    :type f: file
    :param dep: package/dependency object
    :type dep: Dep
    :param dep: package/dependency object
    :type dep: PkgDep
    :return: updated package/dependency object
    :rtype: PkgDep
    """
    pkg_name = UNDEFINED
    dep_name = UNDEFINED

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
    """
    Parse the package information and dependency files.
    Returns the object containing all these information.
    :param info_file_name: package information file name
    :type info_file_name: str
    :param dep_file_name: package dependency file name
    :type dep_file_name: str
    :return: package/dependency object
    :rtype: PkgDep
    """
    dep = PkgDep()

    with open(info_file_name, 'r') as f_info, open(dep_file_name, 'r') as f_dep:
        dep = parse_info_file(f_info, dep)
        dep = parse_dep_file(f_dep, dep)

    return dep


if __name__ == '__main__':
    logging.basicConfig(level=logging.ERROR)
    p_dep = parse_files('pkg.info', 'pkg.dep')
    p_dep.print_packages_and_dependencies()
