%define _localstatedir /var/lib
%define _bindir %{_libdir}/%{name}/bin
%define _sysconfdir /etc/%{name}

%if %{?mdkversion:0}%{?!mdkversion:1}
%global notmdk 1
%endif

Name:		rancid
Version:	2.3.2
Release:	%mkrel 1
Summary:	Really Awesome New Cisco confIg Differ
Group:		Monitoring
License:	GPL
URL:		http://www.shrubbery.net/rancid/
Source:		ftp://ftp.shrubbery.net/pub/rancid/rancid-%{version}.tar.gz
Source1:	README.rancid.urpmi
Requires:	cvs expect >= 5.40
BuildRequires:	expect >= 5.40
Requires(pre):	%{?!notmdk:rpm-helper}%{?notmdk:/usr/sbin/useradd}
Requires(postun):	%{?!notmdk:rpm-helper}%{?notmdk:/usr/sbin/userdel}
BuildRoot:	%{_tmppath}/%{name}-%{version}-root

%description
RANCID monitors a router's (or more generally a device's) configuration,
including software and hardware (cards, serial numbers, etc) and uses CVS
(Concurrent Version System) or Subversion  to maintain history of changes.

RANCID does this by the very simple process summarized here:

    * login to each device in the router table (router.db),
    * run various commands to get the information that will be saved,
    * cook the output; re-format, remove oscillating or incrementing data,
    * email any differences (sample) from the previous collection to a mail
      list,
    * and finally commit those changes to the reivision control system

RANCID also includes looking glass software. It is based on Ed Kern's looking
glass which was once used for http://nitrous.digex.net/, for the old-school
folks who remember it. Our version has added functions, supports cisco,
juniper, and foundry and uses the login scripts that come with rancid; so it
can use telnet or ssh to connect to your devices(s).

Rancid currently supports Cisco routers, Juniper routers, Catalyst switches,
Foundry switches, Redback NASs, ADC EZT3 muxes, MRTd (and thus likely IRRd),
Alteon switches, and HP Procurve switches and a host of others.

Rancid is known to be used at: AOL, Global Crossing, MFN, NTT America,
Certainty Solutions Inc. 

%prep
%setup -q
cp %{SOURCE1} README.urpmi

%build
%configure
%make

%install
rm -Rf %{buildroot}
mkdir -p %{buildroot}/%{_sysconfdir}/ %{buildroot}/%{_localstatedir}/%{name}
%makeinstall_std
perl -pi -e 's/^([^#\$])/# $1/g' %{buildroot}/%{_datadir}/%{name}/cloginrc.sample

perl -pi -e 's,^BASEDIR=%{_localstatedir},BASEDIR=%{_localstatedir}/%{name},g;s,/usr/bin\;,%{_sbindir}\;,' %{buildroot}/%{_sysconfdir}/rancid.conf

mkdir -p %{buildroot}/%{_sysconfdir}/../cron.d/
cat << EOF >> %{buildroot}/%{_sysconfdir}/../cron.d/%{name}
# Rancid cron jobs

# Run config differ hourly
1 * * * * rancid %{_libdir}/rancid/rancid-run

# Clean out config differ logs
50 23 * * * rancid /usr/bin/find /var/lib/rancid/logs -type f -mtime +2 -exec rm {} \;
EOF

%clean
rm -Rf %{buildroot}

%pre
%_pre_useradd %{name} %{_localstatedir}/%{name} /bin/false

%postun
%_postun_userdel %{name}

%files
%defattr(-,root,root)
%dir %{_sysconfdir}
%config(noreplace) %{_sysconfdir}/*
%config(noreplace) %{_sysconfdir}/../cron.d/%{name}
%{_libdir}/%{name}
%{_datadir}/%{name}
%attr(750,rancid,rancid) %{_localstatedir}/%{name}
%doc %{_mandir}/man?/*
%doc README README.lg share/README.misc README.urpmi


