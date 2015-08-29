#
# spec file for DsRomsManager
#
# Written by Fortunato Ventre <vorione@gmail.com>
#

Name:           dsromsmanager
Version:        1.6
Release:        1%{?dist}
Summary:        An utility to manage Nintendo DS roms

Group:          Amusements/Games
License:        GPLv3+
URL:            http://www.voria.org/dsromsmanager
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
* Sat Aug 29 2015 Fortunato Ventre <vorione@gmail.com>
- Packaged for Fedora 22
