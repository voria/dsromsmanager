install:
	mkdir -p $(DESTDIR)/usr/share/dsromsmanager/
	cp src/*.py $(DESTDIR)/usr/share/dsromsmanager/
	cp -r data/ $(DESTDIR)/usr/share/dsromsmanager/
	mkdir -p $(DESTDIR)/usr/share/locale/it/
	cp -r po/locale/it/* $(DESTDIR)/usr/share/locale/it/
	mkdir -p $(DESTDIR)/usr/share/applications/
	cp dsromsmanager.desktop $(DESTDIR)/usr/share/applications/
	mkdir -p $(DESTDIR)/usr/bin/
	cp drm $(DESTDIR)/usr/bin/
	chown root:root $(DESTDIR)/usr/bin/drm
	chmod 755 $(DESTDIR)/usr/bin/drm

uninstall:
	rm -rf $(DESTDIR)/usr/bin/drm
	rm -rf $(DESTDIR)/usr/share/applications/dsromsmanager.desktop
	rm -rf $(DESTDIR)/usr/share/locale/it/LC_MESSAGES/DsRomsManager.po 
	rm -rf $(DESTDIR)/usr/share/dsromsmanager/




