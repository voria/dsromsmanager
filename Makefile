install_dir=install -d -m 755
install_file=install -m 644
install_script=install -m 755

install:
	$(install_dir) $(DESTDIR)/usr/share/dsromsmanager/
	$(install_file) src/*.py $(DESTDIR)/usr/share/dsromsmanager/
	$(install_dir) $(DESTDIR)/usr/share/dsromsmanager/data/images/
	$(install_file) data/images/* $(DESTDIR)/usr/share/dsromsmanager/data/images
	$(install_file) data/dsromsmanager.glade $(DESTDIR)/usr/share/dsromsmanager/data/
	$(install_dir) $(DESTDIR)/usr/share/locale/it/LC_MESSAGES/
	$(install_file) po/locale/it/LC_MESSAGES/* $(DESTDIR)/usr/share/locale/it/LC_MESSAGES/
	$(install_dir) $(DESTDIR)/usr/share/applications/
	$(install_file) dsromsmanager.desktop $(DESTDIR)/usr/share/applications/
	$(install_dir) $(DESTDIR)/usr/bin/
	$(install_script) dsromsmanager $(DESTDIR)/usr/bin/

uninstall:
	rm -rf $(DESTDIR)/usr/bin/dsromsmanager
	rm -rf $(DESTDIR)/usr/share/applications/dsromsmanager.desktop
	rm -rf $(DESTDIR)/usr/share/locale/it/LC_MESSAGES/dsromsmanager.po 
	rm -rf $(DESTDIR)/usr/share/dsromsmanager/
