install_dir=install -d -m 755
install_file=install -m 644
install_script=install -m 755

install:
	$(install_dir) $(DESTDIR)/usr/share/dsromsmanager/
	$(install_file) src/*.py $(DESTDIR)/usr/share/dsromsmanager/
	$(install_dir) $(DESTDIR)/usr/share/dsromsmanager/data/images/
	$(install_file) data/images/* $(DESTDIR)/usr/share/dsromsmanager/data/images
	$(install_file) data/drm.glade $(DESTDIR)/usr/share/dsromsmanager/data/
	$(install_dir) $(DESTDIR)/usr/share/locale/it/
	$(install_file) po/locale/it/* $(DESTDIR)/usr/share/locale/it/
	$(install_dir) $(DESTDIR)/usr/share/applications/
	$(install_file) dsromsmanager.desktop $(DESTDIR)/usr/share/applications/
	$(install_dir) $(DESTDIR)/usr/bin/
	$(install_script) drm $(DESTDIR)/usr/bin/

uninstall:
	rm -rf $(DESTDIR)/usr/bin/drm
	rm -rf $(DESTDIR)/usr/share/applications/dsromsmanager.desktop
	rm -rf $(DESTDIR)/usr/share/locale/it/LC_MESSAGES/dsromsmanager.po 
	rm -rf $(DESTDIR)/usr/share/dsromsmanager/
