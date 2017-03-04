#
# spec file for DsRomsManager
#
# Written by Fortunato Ventre <vorione@gmail.com>
#

Name:           dsromsmanager
Version:        1.6.3
Release:        1%{?dist}
Summary:        An utility to manage Nintendo DS roms

Group:          Amusements/Games
License:        GPLv3+
URL:            https://github.com/voria/dsromsmanager
Source0:        http://www.voria.org/files/nds/%{name}/%{name}-%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

Requires:       pygtk2

%description
DsRomsManager is an utility to manager Nintendo DS roms.

%prep
%setup -q

%build
make

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%files
%{_bindir}/*
%{_datadir}/%{name}/
%{_datadir}/applications/%{name}.desktop
%lang(it) %{_datadir}/locale/it/LC_MESSAGES/%{name}*
%doc README LICENSE

%changelog
* Sat Mar 04 2017 Fortunato Ventre <vorione@gmail.com> - 1.6.3-1
- Handle error when downloading images in a non-existing directory for a single game.

* Sat Mar 04 2017 Fortunato Ventre <vorione@gmail.com> - 1.6.2-1
- Handle error when downloading images in a non-existing directory.
- Other minor fixes and changes.

* Fri Mar 03 2017 Fortunato Ventre <vorione@gmail.com> - 1.6.1-1
- Fix short country code for Denmark

* Sat Aug 29 2015 Fortunato Ventre <vorione@gmail.com> - 1.6-1
- Packaged for Fedora 22
