Name:           openvswitch
Version:        1.7.1
Release:        6%{?dist}
Summary:        Open vSwitch daemon/database/utilities

# Nearly all of openvswitch is ASL 2.0.  The bugtool is LGPLv2+, and the
# lib/sflow*.[ch] files are SISSL
# datapath/ is GPLv2 (although not built into any of the binary packages)
# python/compat is Python (although not built into any of the binary packages)
License:        ASL 2.0 and LGPLv2+ and SISSL
URL:            http://openvswitch.org
Source0:        http://openvswitch.org/releases/%{name}-%{version}.tar.gz
Source1:        openvswitch.service
Source2:        openvswitch.init
Source3:        openvswitch.logrotate
Source4:        ifup-ovs
Source5:        ifdown-ovs
Source6:        ovsdbmonitor.desktop
Source7:        openvswitch-configure-ovskmod-var.patch
# make the kmod name configurable since Fedora kernel ships openvswitch module
# Source7 is not applied, it's used to generate patch0
Patch0:         openvswitch-configure-ovskmod-var-autoconfd.patch
Patch1:         openvswitch-ovs-pki-perm.patch
Patch2:         openvswitch-ovs-ctl-ulimit.patch

BuildRequires:  systemd-units openssl openssl-devel
BuildRequires:  python python-twisted-core python-twisted-conch python-zope-interface PyQt4
BuildRequires:  desktop-file-utils
BuildRequires:  groff graphviz

Requires:       openssl iproute module-init-tools

Requires(post):  systemd
Requires(preun): systemd
Requires(postun): systemd

%description
Open vSwitch provides standard network bridging functions and
support for the OpenFlow protocol for remote per-flow control of
traffic.

%package -n python-openvswitch
Summary:        Open vSwitch python bindings
License:        ASL 2.0
BuildArch:      noarch
Requires:       python

%description -n python-openvswitch
Python bindings for the Open vSwitch database

%package -n ovsdbmonitor
Summary:        Open vSwitch graphical monitoring tool
License:        ASL 2.0
BuildArch:      noarch
Requires:       python-openvswitch = %{version}-%{release}
Requires:       python python-twisted-core python-twisted-conch python-zope-interface PyQt4

%description -n ovsdbmonitor
A GUI tool for monitoring and troubleshooting local or remote Open
vSwitch installations.  It presents GUI tables that graphically represent
an Open vSwitch kernel flow table (similar to "ovs-dpctl dump-flows")
and Open vSwitch database contents (similar to "ovs-vsctl list <table>").

%package test
Summary:        Open vSwitch testing utilities
License:        ASL 2.0
BuildArch:      noarch
Requires:       python-openvswitch = %{version}-%{release}
Requires:       python python-twisted-core python-twisted-web

%description test
Utilities that are useful to diagnose performance and connectivity
issues in Open vSwitch setup.

%package controller
Summary:        Open vSwitch OpenFlow controller
License:        ASL 2.0
Requires:       openvswitch = %{version}-%{release}

%description controller
Simple reference implementation of an OpenFlow controller for Open
vSwitch. Manages any number of remote switches over OpenFlow protocol,
causing them to function as L2 MAC-learning switches or hub.

%prep
%setup -q
%patch0 -p1 -b .ovskmod
%patch1 -p1 -b .openvswitch-ovs-pki-perm
%patch2 -p1 -b .openvswitch-ovs-ctl-ulimit

%build
%configure --enable-ssl --with-pkidir=%{_sharedstatedir}/openvswitch/pki OVSKMOD=openvswitch
make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

install -d -m 0755 $RPM_BUILD_ROOT%{_sysconfdir}/openvswitch

src=rhel/usr_share_openvswitch_scripts_sysconfig.template
dst=$RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/openvswitch
install -p -D -m 0644 $src $dst

install -p -D -m 0644 %{SOURCE1} $RPM_BUILD_ROOT%{_unitdir}/openvswitch.service
install -p -D -m 0755 %{SOURCE2} $RPM_BUILD_ROOT%{_datadir}/openvswitch/scripts/openvswitch.init
install -p -D -m 0644 %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/logrotate.d/openvswitch

install -d -m 0755 $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/network-scripts/
install -p -m 0755 %{SOURCE4} %{SOURCE5} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/network-scripts/

install -d -m 0755 $RPM_BUILD_ROOT/%{_sharedstatedir}/openvswitch

install -d -m 0755 $RPM_BUILD_ROOT%{python_sitelib}
mv $RPM_BUILD_ROOT/%{_datadir}/openvswitch/python/* $RPM_BUILD_ROOT%{python_sitelib}
rmdir $RPM_BUILD_ROOT/%{_datadir}/openvswitch/python/

# Get rid of stuff we don't want to make RPM happy.
rm -f \
    $RPM_BUILD_ROOT%{_sbindir}/ovs-vlan-bug-workaround \
    $RPM_BUILD_ROOT%{_mandir}/man8/ovs-vlan-bug-workaround.8 \
    $RPM_BUILD_ROOT%{_sbindir}/ovs-brcompatd \
    $RPM_BUILD_ROOT%{_mandir}/man8/ovs-brcompatd.8

desktop-file-install --dir=$RPM_BUILD_ROOT%{_datadir}/applications %{SOURCE6}

%post
# Initial installation
%systemd_post openvswitch.service

%preun
# Package removal, not upgrade
%systemd_preun openvswitch.service

%postun
# Package upgrade, not uninstall
%systemd_postun_with_restart openvswitch.service


%files
%{_sysconfdir}/openvswitch/
%config(noreplace) %{_sysconfdir}/logrotate.d/openvswitch
%config(noreplace) %{_sysconfdir}/sysconfig/openvswitch
%{_sysconfdir}/sysconfig/network-scripts/ifup-ovs
%{_sysconfdir}/sysconfig/network-scripts/ifdown-ovs
%{_unitdir}/openvswitch.service
%{_bindir}/ovs-appctl
%{_bindir}/ovs-benchmark
%{_bindir}/ovs-dpctl
%{_bindir}/ovs-ofctl
%{_bindir}/ovs-parse-leaks
%{_bindir}/ovs-pcap
%{_bindir}/ovs-pki
%{_bindir}/ovs-tcpundump
%{_bindir}/ovs-vsctl
%{_bindir}/ovsdb-client
%{_bindir}/ovsdb-tool
# ovs-bugtool is LGPLv2+
%{_sbindir}/ovs-bugtool
%{_sbindir}/ovs-vswitchd
%{_sbindir}/ovsdb-server
%{_mandir}/man1/ovs-benchmark.1*
%{_mandir}/man1/ovs-pcap.1*
%{_mandir}/man1/ovs-tcpundump.1*
%{_mandir}/man1/ovsdb-client.1*
%{_mandir}/man1/ovsdb-server.1*
%{_mandir}/man1/ovsdb-tool.1*
%{_mandir}/man5/ovs-vswitchd.conf.db.5*
%{_mandir}/man8/ovs-appctl.8*
%{_mandir}/man8/ovs-bugtool.8*
%{_mandir}/man8/ovs-ctl.8*
%{_mandir}/man8/ovs-dpctl.8*
%{_mandir}/man8/ovs-ofctl.8*
%{_mandir}/man8/ovs-parse-leaks.8*
%{_mandir}/man8/ovs-pki.8*
%{_mandir}/man8/ovs-vsctl.8*
%{_mandir}/man8/ovs-vswitchd.8*
# /usr/share/openvswitch/bugtool-plugins and
# /usr/share/openvswitch/scripts/ovs-bugtool* are LGPLv2+
%{_datadir}/openvswitch/
%{_sharedstatedir}/openvswitch
# see COPYING for full licensing details
%doc COPYING DESIGN INSTALL.SSL NOTICE README WHY-OVS rhel/README.RHEL

%files -n python-openvswitch
%{python_sitelib}/ovs
%doc COPYING

%files -n ovsdbmonitor
%{_bindir}/ovsdbmonitor
%{_mandir}/man1/ovsdbmonitor.1*
%{_datadir}/ovsdbmonitor
%{_datadir}/applications/ovsdbmonitor.desktop
%doc ovsdb/ovsdbmonitor/COPYING

%files test
%{_bindir}/ovs-test
%{_bindir}/ovs-vlan-test
%{_mandir}/man8/ovs-test.8*
%{_mandir}/man8/ovs-vlan-test.8*
%{python_sitelib}/ovstest

%files controller
%{_bindir}/ovs-controller
%{_mandir}/man8/ovs-controller.8*


%changelog
* Tue Nov 20 2012 Thomas Graf <tgraf@redhat.com> - 1.7.1-6
- Increase max fd limit to support 256 bridges (#873072)

* Tue Nov  1 2012 Thomas Graf <tgraf@redhat.com> - 1.7.1-5
- Don't create world writable pki/*/incomming directory (#845351)

* Tue Oct 25 2012 Thomas Graf <tgraf@redhat.com> - 1.7.1-4
- Don't add iptables accept rule for -p GRE as GRE tunneling is unsupported

* Tue Oct 16 2012 Thomas Graf <tgraf@redhat.com> - 1.7.1-3
- require systemd instead of systemd-units to use macro helpers (#850258)

* Tue Oct  9 2012 Thomas Graf <tgraf@redhat.com> - 1.7.1-2
- make ovs-vsctl timeout if daemon is not running (#858722)

* Mon Sep 10 2012 Thomas Graf <tgraf@redhat.com> - 1.7.1.-1
- Update to 1.7.1

* Fri Sep  7 2012 Thomas Graf <tgraf@redhat.com> - 1.7.0.-3
- add controller package containing ovs-controller

* Thu Aug 23 2012 Tomas Hozza <thozza@redhat.com> - 1.7.0-2
- fixed SPEC file so it comply with new systemd-rpm macros guidelines (#850258)

* Fri Aug 17 2012 Tomas Hozza <thozza@redhat.com> - 1.7.0-1
- Update to 1.7.0
- Fixed openvswitch-configure-ovskmod-var-autoconfd.patch because
  openvswitch kernel module name changed in 1.7.0
- Removed Source8: ovsdbmonitor-move-to-its-own-data-directory.patch
- Patches merged:
  - ovsdbmonitor-move-to-its-own-data-directory-automaked.patch
  - openvswitch-rhel-initscripts-resync.patch

* Fri Jul 20 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 1.4.0-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Mar 15 2012 Chris Wright <chrisw@redhat.com> - 1.4.0-5
- fix ovs network initscripts DHCP address acquisition (#803843)

* Tue Mar  6 2012 Chris Wright <chrisw@redhat.com> - 1.4.0-4
- make BuildRequires openssl explicit (needed on f18/rawhide now)

* Tue Mar  6 2012 Chris Wright <chrisw@redhat.com> - 1.4.0-3
- use glob to catch compressed manpages

* Fri Mar  1 2012 Chris Wright <chrisw@redhat.com> - 1.4.0-2
- Update License comment, use consitent macros as per review comments bz799171

* Wed Feb 29 2012 Chris Wright <chrisw@redhat.com> - 1.4.0-1
- Initial package for Fedora
