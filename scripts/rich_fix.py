from pathlib import Path
p=Path('takeover-v2.js')
s=p.read_text()
bad="$('#accountFeatureFile').onchange=e=>{const f=e.target.files?.[0];if(f)setLogoPreview('#accountFeaturePreview','#accountFeatureFile',URL.createObjectURL(f),'NO FEATURE IMAGE')};if(f)setLogoPreview('#accountLogoPreview','#accountLogo',URL.createObjectURL(f),'NO LOGO YET')};"
good="$('#accountFeatureFile').onchange=e=>{const f=e.target.files?.[0];if(f)setLogoPreview('#accountFeaturePreview','#accountFeatureFile',URL.createObjectURL(f),'NO FEATURE IMAGE')};"
if bad not in s:
    raise SystemExit('expected duplicate account-logo tail not found')
p.write_text(s.replace(bad,good,1))
