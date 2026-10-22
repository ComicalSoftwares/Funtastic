pkgdatadir = get_option('prefix') / get_option('datadir') / meson.project_name()
moduledir = pkgdatadir / 'funtastic'
gnome = import('gnome')

gnome.compile_resources('funtastic',
  'funtastic.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').full_path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', get_option('prefix') / get_option('localedir'))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'funtastic.in',
  output: 'funtastic',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir'),
  install_mode: 'rwxr-xr-x'
)

funtastic_sources = [
  '__init__.py',
  'main.py',
  'window.py',
  'preferences.py'
]

install_data(funtastic_sources, install_dir: moduledir)
