install:
	mkdir -p $(DESTDIR)/usr/share/dsromsmanager/
	cp src/*.py $(DESTDIR)/usr/share/dsromsmanager/
	cp -r data/ $(DESTDIR)/usr/share/dsromsmanager/
	mkdir -p $(DESTDIR)/usr/share/applications/
	cp dsromsmanager.desktop $(DESTDIR)/usr/share/applications/
	cp drm $(DESTDIR)/usr/bin/

uninstall:
	rm -rf $(DESTDIR)/usr/bin/drm
	rm -rf $(DESTDIR)/usr/share/applications/dsromsmanager.desktop
	rm -rf $(DESTDIR)/usr/share/dsromsmanager/




