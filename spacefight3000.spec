# -*- mode: python -*-
a = Analysis(['spacefight3000.py'],
             pathex=['c:\\Users\\Paul\\Documents\\spacefight3000'],
             hiddenimports=[],
             hookspath=None,
             runtime_hooks=None)
pyz = PYZ(a.pure)
exe = EXE(pyz,
          a.scripts,
          exclude_binaries=True,
          name='spacefight3000.exe',
          debug=False,
          strip=None,
          upx=True,
          console=True )
image_tree = Tree('resource', prefix='resource')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
	       image_tree,
               strip=None,
               upx=True,
               name='spacefight3000')

