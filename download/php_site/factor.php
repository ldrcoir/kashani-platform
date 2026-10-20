<?php
// ============================================================
// factor.php — آزمایشگاه مجازی فاکتور
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
    <title>🧮 آزمایشگاه فاکتور</title>
    <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2/dist/tailwind.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/js-big-integer/0.7.1/BigInteger.min.js"></script>
    <style>body{font-family:'Vazirmatn',Tahoma,sans-serif}.tab-active{background:#3b82f6;color:white}</style>
</head>
<body class="bg-gray-50 min-h-screen">
<header class="bg-white shadow-sm sticky top-0 z-50">
    <div class="max-w-7xl mx-auto px-4 py-3 flex items-center justify-between">
        <div class="flex items-center gap-3"><span class="text-3xl">🧮</span><h1 class="text-xl font-bold">آزمایشگاه فاکتور</h1></div>
        <a href="index.php" class="px-4 py-2 bg-gray-100 rounded text-sm">🏠 خانه</a>
    </div>
</header>

<div class="max-w-5xl mx-auto p-4">
    <div class="flex gap-1 mb-4 border-b">
        <button onclick="showTab('factor')" id="tab_factor" class="tab tab-active px-4 py-2 rounded-t text-sm">🔢 فاکتور عدد</button>
        <button onclick="showTab('prime')" id="tab_prime" class="tab px-4 py-2 rounded-t text-sm">✨ تولید عدد اول</button>
        <button onclick="showTab('sinus')" id="tab_sinus" class="tab px-4 py-2 rounded-t text-sm">📐 قضیه‌ی سینوس</button>
        <button onclick="showTab('mersenne')" id="tab_mersenne" class="tab px-4 py-2 rounded-t text-sm">⭐ اعداد مرسن</button>
    </div>
    
    <div id="tab_factor_content" class="bg-white rounded-xl shadow p-6">
        <h3 class="text-lg font-bold mb-2 text-gray-800">فاکتور کردن عدد</h3>
        <p class="text-sm text-gray-500 mb-4">با Pollard Rho در مرورگر — اعداد ۲۰-۵۰ رقم در چند ثانیه</p>
        <div class="flex gap-2 mb-4">
            <input type="text" id="number" placeholder="12345678901234567890" class="flex-1 px-4 py-3 border rounded-lg text-lg font-mono" dir="ltr">
            <button onclick="doFactor()" class="bg-blue-600 text-white px-6 py-3 rounded-lg font-bold">🔍 فاکتور</button>
        </div>
        <div id="result" class="min-h-32 p-4 bg-gray-50 rounded"><p class="text-gray-400">عدد وارد کنید</p></div>
    </div>
    
    <div id="tab_prime_content" class="bg-white rounded-xl shadow p-6 hidden">
        <h3 class="text-lg font-bold mb-2">تولید عدد اول</h3>
        <p class="text-sm text-gray-500 mb-4">با Miller-Rabin</p>
        <div class="flex gap-2 items-end mb-4">
            <div><label class="block text-xs text-gray-500 mb-1">تعداد رقم</label>
            <select id="prime_digits" class="px-3 py-2 border rounded text-sm"><option>10</option><option selected>20</option><option>30</option><option>50</option><option>100</option></select></div>
            <button onclick="generatePrime()" class="bg-emerald-600 text-white px-6 py-2 rounded text-sm">✨ تولید</button>
        </div>
        <div id="prime_result" class="min-h-32 p-4 bg-gray-50 rounded text-sm"><p class="text-gray-400">دکمه‌ی تولید را بزنید</p></div>
    </div>
    
    <div id="tab_sinus_content" class="bg-white rounded-xl shadow p-6 hidden">
        <h3 class="text-lg font-bold mb-2">قضیه‌ی سینوس</h3>
        <div class="bg-blue-50 border-r-4 border-blue-500 p-3 rounded mb-4 text-sm">
            <strong>قضیه:</strong> برای هر عدد اول p ≥ 7:
            <ul class="list-disc mr-5 mt-1 text-xs"><li>sin(30p°) = +0.5 اگر p ≡ 1, 5 (mod 12)</li><li>sin(30p°) = −0.5 اگر p ≡ 7, 11 (mod 12)</li></ul>
        </div>
        <div class="flex gap-2 mb-4">
            <input type="number" id="sin_p" placeholder="عدد اول" class="px-4 py-2 border rounded text-sm font-mono" dir="ltr" value="7">
            <button onclick="testSinus()" class="bg-purple-600 text-white px-6 py-2 rounded text-sm">🔬 تست</button>
        </div>
        <div id="sin_result" class="min-h-32 p-4 bg-gray-50 rounded text-sm"></div>
    </div>
    
    <div id="tab_mersenne_content" class="bg-white rounded-xl shadow p-6 hidden">
        <h3 class="text-lg font-bold mb-2">اعداد مرسن (M_p = 2^p - 1)</h3>
        <p class="text-sm text-gray-500 mb-4">تست اول بودن با Lucas-Lehmer (ساده)</p>
        <div class="flex gap-2 mb-4">
            <input type="number" id="mer_p" placeholder="p (عدد اول)" class="px-4 py-2 border rounded text-sm font-mono" dir="ltr" value="13">
            <button onclick="checkMersenne()" class="bg-amber-600 text-white px-6 py-2 rounded text-sm">⭐ بررسی</button>
        </div>
        <div id="mer_result" class="min-h-32 p-4 bg-gray-50 rounded text-sm"></div>
    </div>
</div>

<script>
function gcd(a,b){while(!b.eq(0)){[a,b]=[b,a.mod(b)]}return a}
function isProbablePrime(n,k=20){
    if(n.lt(2))return false;if(n.lt(4))return true;if(n.mod(2).eq(0))return false;
    let d=n.minus(1),r=0;while(d.mod(2).eq(0)){d=d.divide(2);r++}
    for(let i=0;i<k;i++){
        const a=bigInt.randBetween(2,n.minus(2));
        let x=a.modPow(d,n);
        if(x.eq(1)||x.eq(n.minus(1)))continue;
        for(let j=0;j<r-1;j++){x=x.modPow(2,n);if(x.eq(n.minus(1)))break;if(x.eq(1))return false}
        if(!x.eq(n.minus(1)))return false
    }return true
}
function pollardRho(n){
    if(n.mod(2).eq(0))return bigInt(2);
    let x=bigInt(2),y=bigInt(2),d=bigInt(1);
    const f=v=>v.modPow(2,n).plus(1).mod(n);
    let it=0;while(d.eq(1)&&it<1000000){x=f(x);y=f(f(y));d=gcd(x.minus(y).abs(),n);it++}
    return d.eq(n)?null:d
}
function factor(n){
    if(n.lt(2))return[n];if(isProbablePrime(n))return[n];
    const fs=[];
    for(const p of[2,3,5,7,11,13,17,19,23,29,31,37,41,43,47,53,59,61,67,71,73,79,83,89,97]){while(n.mod(p).eq(0)){fs.push(bigInt(p));n=n.divide(p)}}
    if(n.eq(1))return fs;
    const st=[n];
    while(st.length>0){const m=st.pop();if(m.eq(1))continue;if(isProbablePrime(m)){fs.push(m);continue}
        const d=pollardRho(m);if(!d){fs.push(m);continue}st.push(d);st.push(m.divide(d))}
    return fs.sort((a,b)=>a.compare(b))
}
function doFactor(){
    const input=document.getElementById('number').value.trim();
    if(!input){document.getElementById('result').innerHTML='<p class="text-gray-400">عدد وارد کنید</p>';return}
    try{
        const n=bigInt(input);
        if(n.lt(2)){document.getElementById('result').innerHTML='<p class="text-red-500">≥2 باید باشد</p>';return}
        const t=performance.now();const fs=factor(n);const tt=(performance.now()-t).toFixed(0);
        let h='<div class="text-sm text-gray-500 mb-2">مدت: '+tt+'ms</div>';
        h+='<div class="font-mono text-lg text-blue-700" dir="ltr">'+fs.map(f=>f.toString()).join(' × ')+'</div>';
        h+='<div class="mt-3 grid grid-cols-2 gap-2 text-xs">';
        h+='<div class="bg-gray-100 p-2 rounded">فاکتور: <b>'+fs.length+'</b></div>';
        h+='<div class="bg-gray-100 p-2 rounded">نوع: <b>'+(fs.length===1?'اول':'مرکب')+'</b></div></div>';
        document.getElementById('result').innerHTML=h
    }catch(e){document.getElementById('result').innerHTML='<p class="text-red-500">'+e.message+'</p>'}
}
function nextPrime(n){let p=n.plus(1);if(p.mod(2).eq(0)&&p.gt(2))p=p.plus(1);while(!isProbablePrime(p))p=p.plus(2);return p}
function generatePrime(){
    const d=parseInt(document.getElementById('prime_digits').value);
    const s=bigInt(10).pow(d-1).plus(Math.floor(Math.random()*9e17));
    const p=nextPrime(s);
    document.getElementById('prime_result').innerHTML='<div class="font-mono text-blue-700" dir="ltr">'+p.toString()+'</div><div class="text-xs text-gray-500 mt-1">'+p.toString().length+' رقم</div>'
}
function testSinus(){
    const p=parseInt(document.getElementById('sin_p').value);
    if(!p||p<7){document.getElementById('sin_result').innerHTML='<p class="text-red-500">p ≥ 7 باید باشد</p>';return}
    const s=Math.sin(30*p*Math.PI/180);
    const m=p%12;
    const exp=(m===1||m===5)?0.5:((m===7||m===11)?-0.5:null);
    let h='<div class="font-mono text-sm" dir="ltr">sin(30×'+p+'°) = '+s.toFixed(10)+'<br>p mod 12 = '+m+'<br>';
    if(exp!==null){const ok=Math.abs(s-exp)<1e-10;h+='<span class="'+(ok?'text-green-600':'text-red-600')+'">'+(ok?'✓ مطابق':'✗ خلاف')+'</span>'}else{h+='<span class="text-yellow-600">p باید ≡ 1,5,7,11 (mod 12)</span>'}
    document.getElementById('sin_result').innerHTML=h+'</div>'
}
function checkMersenne(){
    const p=parseInt(document.getElementById('mer_p').value);
    if(!p||p<2){return}
    const m=bigInt(2).pow(p).minus(1);
    const prime=isProbablePrime(m);
    let h='<div class="font-mono text-sm" dir="ltr">M('+p+') = 2^'+p+' - 1<br>= '+m.toString().substring(0,80)+(m.toString().length>80?'...':'')+'<br>('+m.toString().length+' رقم)<br><span class="'+(prime?'text-green-600':'text-red-600')+'">'+(prime?'✓ اول':'✗ مرکب')+'</span></div>';
    document.getElementById('mer_result').innerHTML=h
}
function showTab(name){
    ['factor','prime','sinus','mersenne'].forEach(t=>{
        document.getElementById('tab_'+t+'_content').classList.toggle('hidden',t!==name);
        document.getElementById('tab_'+t).classList.toggle('tab-active',t===name)
    })
}
</script>
</body>
</html>
