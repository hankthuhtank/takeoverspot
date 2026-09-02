from pathlib import Path
p=Path('takeover-v3.css'); s=p.read_text()
marker='/* TAKEOVER V22.1 DESKTOP TYPE COMPLETION */'
if marker not in s:
    s += '''\n\n/* TAKEOVER V22.1 DESKTOP TYPE COMPLETION */
@media(min-width:901px){
.site-legal a{font-size:9.5px!important;padding:7px 9px!important}
.rule b{font-size:14px!important;line-height:1.35!important}.rule span{font-size:12px!important;line-height:1.5!important}
.canvas-open{font-size:11px!important;padding:10px 13px!important}.canvas-no-login{font-size:11.5px!important}
.preset-title b{font-size:11.5px!important}.preset-title span{font-size:10.5px!important}.preset-card>span{font-size:9px!important;line-height:1.25!important}
.tool-btn{font-size:10.5px!important}.canvas-stage-tip{font-size:9.5px!important}.canvas-section h3{font-size:11px!important}
.canvas-row label{font-size:10.5px!important;min-width:64px!important}.canvas-row input[type="text"],.canvas-row select{font-size:13.5px!important}.canvas-help{font-size:10.5px!important;line-height:1.5!important}
.canvas-save,.canvas-library-save,.canvas-delete{font-size:12px!important}.geometry-grid label{font-size:9px!important}.geometry-grid input{font-size:13px!important}
.territory-card h4{font-size:15px!important}.territory-card small{font-size:11px!important;line-height:1.4!important}.territory-actions button{font-size:9.5px!important}.stat b{font-size:16px!important}.stat span{font-size:9px!important}.spot-chip{font-size:9.5px!important}
.saved-design-meta b{font-size:13px!important}.saved-design-meta span{font-size:10.5px!important}.saved-design-actions button{font-size:9.5px!important}
.admin-console .admin-row b{font-size:15px!important}.admin-console .admin-row small{font-size:11px!important}.admin-block-head b{font-size:12.5px!important}.admin-block-head span{font-size:11px!important}.admin-note{font-size:11px!important}.security-card>span{font-size:10px!important}.security-card small{font-size:11px!important}.support-head span:not(.support-status){font-size:11px!important}.support-head small{font-size:10px!important}.support-status{font-size:9px!important}.support-row p{font-size:12px!important}
.spot-control-card>b{font-size:13px!important}.spot-control-card>span{font-size:12.5px!important}.spot-history-meta>b{font-size:14px!important}.spot-history-meta>span,.spot-history-meta>p{font-size:11.5px!important}
}
'''
p.write_text(s)
p=Path('boot.js'); s=p.read_text().replace("takeover-v3.css?v=22'","takeover-v3.css?v=22.1'"); p.write_text(s)
print('V22.1 typography complete')
