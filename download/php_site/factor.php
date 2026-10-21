<?php
// ============================================================
// factor.php — آزمایشگاه فاکتور (طراحی مدرن، کم‌اسکرول)
// ============================================================
require_once __DIR__ . '/functions.php';
secure_session_start();
$lang = $_GET['lang'] ?? $_COOKIE['lang'] ?? 'fa';
$dir = in_array($lang, ['fa','ar','ur']) ? 'rtl' : 'ltr';
?>
<!DOCTYPE html>
<html lang="<?= $lang ?>" dir="<?= $dir ?>">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link rel="canonical" href="<?= site_url() ?>/factor.php">
<title>🧮 آزمایشگاه فاکتور</title>
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/js-big-integer/0.7.1/BigInteger.min.js"></script>
<style>
body{font-family:'Vazirmatn',sans-serif}
.tab-active{background:#3b82f6;color:white}
.card{transition:all 0.2s}
.card:hover{box-shadow:0 8px 20px rgba(0,0,0,0.1)}
</style>
</head>
<body class="bg-gray-50 min-h-screen">
<header class="bg-white shadow-sm sticky top-0 z-50">
<div class="max-w-6xl mx-auto px-4 py-2 flex justify-between items-center">
<div class="flex items-center gap-2"><span class="text-2xl">🧮</span><span class="font-bold text-sm">آزمایشگاه</span></div>
<a href="index.php" class="text-xs text-gray-500 hover:text-blue-600">🏠 خانه</a>
</div>
</header>

<div class="max-w-4xl mx-auto p-4">
<!-- Tabs — icon-based, compact -->
<div class="flex gap-1 mb-4">
<button onclick="showTab('factor')" id="tab_factor" class="tab tab-active px-4 py-2 rounded-t text-sm">🔢 فاکتور</button>
<button onclick="showTab('prime')" id="tab_prime" class="tab px-4 py-2 rounded-t text-sm">✨ اول</button>
<button onclick="showTab('mersenne')" id="tab_mersenne" class="tab px-4 py-2 rounded-t text-sm">⭐ مرسن</button>
</div>

<!-- Factor Tab -->
<div id="tab_factor_content" class="bg-white rounded-xl shadow p-6 card">
<h3 class="font-bold mb-2">فاکتور عدد</h3>
<p class="text-xs text-gray-500 mb-3">Pollard Rho در مرورگر — ۲۰-۵۰ رقم در چند ثانیه</p>
<div class="flex gap-2 mb-3">
<input type="text" id="number" placeholder="12345678901234567890" class="flex-1 px-3 py-2 border rounded text-sm font-mono" dir="ltr">
<button onclick="doFactor()" class="bg-blue-600 text-white px-4 py-2 rounded text-sm">🔍</button>
</div>
<div id="result" class="p-3 bg-gray-50 rounded text-sm min-h-20"><p class="text-gray-400">عدد وارد کنید</p></div>
</div>

<!-- Prime Tab -->
<div id="tab_prime_content" class="bg-white rounded-xl shadow p-6 card hidden">
<h3 class="font-bold mb-2">تولید عدد اول</h3>
<div class="flex gap-2 items-end mb-3">
<select id="prime_digits" class="px-2 py-2 border rounded text-sm"><option>10</option><option selected>20</option><option>30</option><option>50</option><option>100</option></select>
<button onclick="generatePrime()" class="bg-emerald-600 text-white px-4 py-2 rounded text-sm">✨ تولید</button>
</div>
<div id="prime_result" class="p-3 bg-gray-50 rounded text-sm min-h-20"></div>
</div>

<!-- Mersenne Tab -->
<div id="tab_mersenne_content" class="bg-white rounded-xl shadow p-6 card hidden">
<h3 class="font-bold mb-2">اعداد مرسن (M_p = 2^p - 1)</h3>
<div class="flex gap-2 mb-3">
<input type="number" id="mer_p" value="13" class="px-3 py-2 border rounded text-sm font-mono" dir="ltr">
<button onclick="checkMersenne()" class="bg-amber-600 text-white px-4 py-2 rounded text-sm">⭐ بررسی</button>
</div>
<div id="mer_result" class="p-3 bg-gray-50 rounded text-sm min-h-20"></div>
</div>
</div>

<script>
function gcd(a,b){while(!b.eq(0)){[a,b]=[b,a.mod(b)]}return a}
function isProbablePrime(n,k=20){if(n.lt(2))return false;if(n.lt(4))return true;if(n.mod(2).eq(0))return false;let d=n.minus(1),r=0;while(d.mod(2).eq(0)){d=d.divide(2);r++}for(let i=0;i<k;i++){const a=bigInt.randBetween(2,n.minus(2));let x=a.modPow(d,n);if(x.eq(1)||x.eq(n.minus(1)))continue;for(let j=0;j<r-1;j++){x=x.modPow(2,n);if(x.eq(n.minus(1)))break;if(x.eq(1))return false}if(!x.eq(n.minus(1)))return false}return true}
function pollardRho(n){if(n.mod(2).eq(0))return bigInt(2);let x=bigInt(2),y=bigInt(2),d=bigInt(1);const f=v=>v.modPow(2,n).plus(1).mod(n);let it=0;while(d.eq(1)&&it<1e6){x=f(x);y=f(f(y));d=gcd(x.minus(y).abs(),n);it++}return d.eq(n)?null:d}
function factor(n){if(n.lt(2))return[n];if(isProbablePrime(n))return[n];const fs=[];for(const p of[2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]){while(n.mod(p).eq(0)){fs.push(bigInt(p));n=n.divide(p)}}if(n.eq(1))return fs;const st=[n];while(st.length>0){const m=st.pop();if(m.eq(1))continue;if(isProbablePrime(m)){fs.push(m);continue}const d=pollardRho(m);if(!d){fs.push(m);continue}st.push(d);st.push(m.divide(d))}return fs.sort((a,b)=>a.compare(b))}
function doFactor(){const input=document.getElementById('number').value.trim();if(!input){document.getElementById('result').innerHTML='<p class="text-gray-400">عدد وارد کنید</p>';return}try{const n=bigInt(input);if(n.lt(2)){document.getElementById('result').innerHTML='<p class="text-red-500">≥2</p>';return}const t=performance.now();const fs=factor(n);const tt=(performance.now()-t).toFixed(0);let h='<div class="text-xs text-gray-500 mb-1">'+tt+'ms</div>';h+='<div class="font-mono text-sm text-blue-700" dir="ltr">'+fs.map(f=>f.toString()).join(' × ')+'</div>';h+='<div class="mt-2 flex gap-2 text-xs"><span class="bg-gray-100 px-2 py-1 rounded">فاکتور: '+fs.length+'</span><span class="bg-gray-100 px-2 py-1 rounded">'+(fs.length===1?'اول':'مرکب')+'</span></div>';document.getElementById('result').innerHTML=h}catch(e){document.getElementById('result').innerHTML='<p class="text-red-500">'+e.message+'</p>'}}
function nextPrime(n){let p=n.plus(1);if(p.mod(2).eq(0)&&p.gt(2))p=p.plus(1);while(!isProbablePrime(p))p=p.plus(2);return p}
function generatePrime(){const d=parseInt(document.getElementById('prime_digits').value);const s=bigInt(10).pow(d-1).plus(Math.floor(Math.random()*9e17));const p=nextPrime(s);document.getElementById('prime_result').innerHTML='<div class="font-mono text-blue-700" dir="ltr">'+p.toString()+'</div><div class="text-xs text-gray-500 mt-1">'+p.toString().length+' رقم</div>'}
function checkMersenne(){const p=parseInt(document.getElementById('mer_p').value);if(!p||p<2)return;const m=bigInt(2).pow(p).minus(1);const prime=isProbablePrime(m);let h='<div class="font-mono text-xs" dir="ltr">M('+p+') = '+m.toString().substring(0,80)+(m.toString().length>80?'...':'')+'<br>('+m.toString().length+' رقم)<br><span class="'+(prime?'text-green-600':'text-red-600')+'">'+(prime?'✓ اول':'✗ مرکب')+'</span></div>';document.getElementById('mer_result').innerHTML=h}
function showTab(n){['factor','prime','mersenne'].forEach(t=>{document.getElementById('tab_'+t+'_content').classList.toggle('hidden',t!==n);document.getElementById('tab_'+t).classList.toggle('tab-active',t===n)})}
</script>
</body>
</html>
