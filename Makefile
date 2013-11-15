PREFIX?=/usr
install_dir=install -d -m 755
install_file=install -pm 644
install_script=install -pm 755

all: trimmer_build

install: manager_install trimmer_install

uninstall: manager_uninstall trimmer_uninstall

manager_install:
	$(shell ./set_prefix.sh $(PREFIX))
	$(install_dir) $(DESTDIR)$(PREFIX)/share/dsromsmanager/
	$(install_file) src/*.py $(DESTDIR)$(PREFIX)/share/dsromsmanager/
	$(install_dir) $(DESTDIR)$(PREFIX)/share/dsromsmanager/data/images/
	$(install_file) data/images/* $(DESTDIR)$(PREFIX)/share/dsromsmanager/data/images
	$(install_file) data/dsromsmanager.glade $(DESTDIR)$(PREFIX)/share/dsromsmanager/data/
	$(install_dir) $(DESTDIR)$(PREFIX)/share/locale/it/LC_MESSAGES/
	$(install_file) po/locale/it/LC_MESSAGES/* $(DESTDIR)$(PREFIX)/share/locale/it/LC_MESSAGES/
	$(install_dir) $(DESTDIR)$(PREFIX)/share/applications/
	$(install_file) dsromsmanager.desktop $(DESTDIR)$(PREFIX)/share/applications/
	$(install_dir) $(DESTDIR)$(PREFIX)/bin/
	$(install_script) dsromsmanager $(DESTDIR)$(PREFIX)/bin/

manager_uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/dsromsmanager
	rm -f $(DESTDIR)$(PREFIX)/share/applications/dsromsmanager.desktop
	rm -f $(DESTDIR)$(PREFIX)/share/locale/it/LC_MESSAGES/dsromsmanager.po
	rm -rf $(DESTDIR)$(PREFIX)/share/dsromsmanager/

trimmer_build:
	gcc dsromstrimmer/dsromstrimmer.c -o dsromstrimmer/dsromstrimmer
	
trimmer_install: trimmer_build
	$(install_dir) $(DESTDIR)$(PREFIX)/bin/
	$(install_script) dsromstrimmer/dsromstrimmer $(DESTDIR)$(PREFIX)/bin/
	
trimmer_uninstall:
	rm -f $(DESTDIR)$(PREFIX)/bin/dsromstrimmer
	
clean:
	rm -f dsromstrimmer/dsromstrimmer
