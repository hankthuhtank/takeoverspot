from pathlib import Path
p=Path('takeover-v3.js')
s=p.read_text()
fixes=[
("function clamp(n,a,b)function clamp(n,a,b)","function clamp(n,a,b)"),
("function openTakeover(n)function openTakeover(n)","function openTakeover(n)"),
("function renderPurchaseCanvasPreview()function renderPurchaseCanvasPreview()","function renderPurchaseCanvasPreview()"),
("function ensureCanvasModal()function ensureCanvasModal()","function ensureCanvasModal()"),
("function selectionShape(nums)function selectionShape(nums)","function selectionShape(nums)"),
("function closeCanvasEditor()function closeCanvasEditor()","function closeCanvasEditor()"),
("function stageDelta(e0,e1)function stageDelta(e0,e1)","function stageDelta(e0,e1)"),
("function renderInspector()function renderInspector()","function renderInspector()"),
("async function saveCanvasEditor()async function saveCanvasEditor()","async function saveCanvasEditor()"),
("async function checkout()async function checkout()","async function checkout()"),
("function openAuth()function openAuth()","function openAuth()"),
("if($('#checkoutBtn'))$('#checkoutBtn').onclick=checkout;if($('#checkoutBtn'))$('#checkoutBtn').onclick=checkout;","if($('#checkoutBtn'))$('#checkoutBtn').onclick=checkout;")
]
for old,new in fixes:s=s.replace(old,new)
p.write_text(s)
print('canvas output boundaries fixed v2')
