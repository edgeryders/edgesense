VERSION=0.99.1
SRCDIR = drupal
BUILDDIR = build
OUTDIR = dist
STATICDIR = ../static

all: makedir staticfiles phpfiles dist

makedir:
	mkdir -p $(BUILDDIR)/edgesense/views
	mkdir -p $(OUTDIR)

staticfiles: makedir
	mkdir -p $(BUILDDIR)/edgesense/static
	cp -f $(STATICDIR)/drupal.html $(BUILDDIR)/edgesense/static/dashboard.html
	cp -f -r $(STATICDIR)/css $(BUILDDIR)/edgesense/static
	cp -f -r $(STATICDIR)/fonts $(BUILDDIR)/edgesense/static
	cp -f -r $(STATICDIR)/img $(BUILDDIR)/edgesense/static
	cp -f -r $(STATICDIR)/js $(BUILDDIR)/edgesense/static
	cp -f -r $(STATICDIR)/json/help.json $(BUILDDIR)/edgesense

phpfiles: makedir
	cp -f -r $(SRCDIR)/edgesense* $(BUILDDIR)/edgesense
	cp -f -r $(SRCDIR)/views/edgesense.* $(BUILDDIR)/edgesense/views

build: makedir staticfiles phpfiles
	
dist: makedir
	cd $(BUILDDIR) && tar -cvzf ../$(OUTDIR)/edgesense_$(VERSION).tgz edgesense 
	cd $(BUILDDIR) && cp ../$(OUTDIR)/edgesense_$(VERSION).tgz ../$(OUTDIR)/edgesense_latest.tgz
clean:
	rm -rf $(BUILDDIR)