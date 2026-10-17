'use strict';
// Blueprint UI behaviour and safer backup/confirmation sheets. Existing Suki storage keys remain unchanged.
(()=>{
  const tabBar=document.querySelector('#tabBar'),detail=document.querySelector('#detail');
  const backupSheet=document.querySelector('#backupSheet'),restoreSheet=document.querySelector('#restoreSheet'),confirmSheet=document.querySelector('#confirmSheet');
  document.querySelectorAll('[data-go]').forEach(button=>{
    const previous=button.onclick;
    button.onclick=event=>{
      if(tabBar.classList.contains('compact')){
        const active=button.classList.contains('active');
        tabBar.classList.remove('compact');
        if(active){event.preventDefault();return}
      }
      if(previous)previous.call(button,event);
      document.querySelectorAll('.nav').forEach(nav=>{
        if(nav.classList.contains('active'))nav.setAttribute('aria-current','page');
        else nav.removeAttribute('aria-current');
      });
      if(detail&&!detail.classList.contains('hide'))detail.classList.add('hide');
      document.body.classList.remove('detail-open');
    };
  });

  let lastY=window.scrollY;
  window.addEventListener('scroll',()=>{
    const y=window.scrollY,delta=y-lastY;lastY=y;
    if(!tabBar||document.querySelector('dialog[open]'))return;
    if(y<120||delta < -3)tabBar.classList.remove('compact');
    else if(delta > 3)tabBar.classList.add('compact');
  },{passive:true});
  if(detail){
    const observer=new MutationObserver(()=>{
      const open=!detail.classList.contains('hide');
      document.body.classList.toggle('detail-open',open);
      tabBar.classList.toggle('detail-hidden',open);
    });
    observer.observe(detail,{attributes:true,attributeFilter:['class']});
  }
  document.addEventListener('gesturestart',event=>event.preventDefault(),{passive:false});
  document.addEventListener('gesturechange',event=>event.preventDefault(),{passive:false});
  document.addEventListener('touchmove',event=>{if(event.touches&&event.touches.length>1)event.preventDefault()},{passive:false});
  document.querySelectorAll('[data-close-dialog]').forEach(button=>button.addEventListener('click',()=>button.closest('dialog')?.close()));

  let confirmResolve=null;
  function confirmAction(title,message,action='Continue'){
    document.querySelector('#confirmTitle').textContent=title;
    document.querySelector('#confirmMessage').textContent=message;
    document.querySelector('#confirmAccept').textContent=action;
    return new Promise(resolve=>{confirmResolve=resolve;confirmSheet.showModal()});
  }
  window.sukiConfirm=confirmAction;
  document.querySelector('#confirmAccept').onclick=()=>{confirmSheet.close();if(confirmResolve){confirmResolve(true);confirmResolve=null}};
  document.querySelector('#confirmCancel').onclick=()=>{confirmSheet.close();if(confirmResolve){confirmResolve(false);confirmResolve=null}};
  confirmSheet.addEventListener('close',()=>{if(confirmResolve){confirmResolve(false);confirmResolve=null}});

  const lastBackupKey='suki:lastBackup';
  function updateBackupDate(){
    const value=localStorage.getItem(lastBackupKey),label=document.querySelector('#lastBackup');
    if(!label)return;
    const reminder=document.querySelector('#backupReminder');
    if(!value){label.textContent='Not backed up yet';if(reminder)reminder.classList.remove('hide');return}
    const date=new Date(value),days=(Date.now()-date.getTime())/86400000;
    label.textContent=Number.isNaN(date.getTime())?'Not backed up yet':days>=14?'Overdue · '+date.toLocaleDateString('en-GB',{day:'numeric',month:'short'}):date.toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric'});
    label.classList.toggle('backup-overdue',days>=14);
    if(reminder){reminder.textContent=days>=14?'Your last backup was over two weeks ago. Open settings to save a fresh copy.':'Your records are backed up.';reminder.classList.toggle('hide',days<14)}
  }
  updateBackupDate();
  if(navigator.storage&&navigator.storage.estimate){
    navigator.storage.estimate().then(info=>{
      const size=document.querySelector('#storageUsed');
      if(size&&Number.isFinite(info.usage))size.textContent=info.usage<1024*1024?Math.max(1,Math.round(info.usage/1024))+' KB':(info.usage/1024/1024).toFixed(1)+' MB';
      else if(size)size.textContent='Not available in this browser';
    }).catch(()=>{const size=document.querySelector('#storageUsed');if(size)size.textContent='Not available in this browser'});
  }
  let preparedBackup=null;
  document.querySelector('#backup').onclick=()=>{
    document.querySelector('#backupHelp').textContent='Preparing your purchases, personal price notes and saved rate.';
    document.querySelector('#saveBackup').disabled=true;
    document.querySelector('#saveBackup').textContent='Preparing…';
    backupSheet.showModal();
    setTimeout(()=>{
      preparedBackup=JSON.stringify({app:'Suki',schemaVersion:1,exportedAt:new Date().toISOString(),purchases,observations,rate},null,2);
      document.querySelector('#backupHelp').textContent='Your backup is ready. Save the file somewhere you can find it later.';
      document.querySelector('#saveBackup').disabled=false;
      document.querySelector('#saveBackup').textContent='Save backup';
    },220);
  };
  document.querySelector('#saveBackup').onclick=()=>{
    if(!preparedBackup)return;
    download('suki-backup-'+today()+'.json',preparedBackup,'application/json');
    localStorage.setItem(lastBackupKey,new Date().toISOString());
    updateBackupDate();backupSheet.close();toast('Backup saved');
  };

  let pendingImport=null;
  const restoreInput=document.querySelector('#restoreFile');
  document.querySelector('#restoreBtn').onclick=()=>restoreInput.click();
  restoreInput.onchange=async event=>{
    const file=event.target.files?.[0];if(!file)return;
    try{
      const data=JSON.parse(await file.text());
      if(data.app!=='Suki'||!Array.isArray(data.purchases)||!Array.isArray(data.observations))throw Error('This does not look like a Suki backup.');
      pendingImport=data;
      const exported=data.exportedAt?new Date(data.exportedAt).toLocaleDateString('en-GB',{day:'numeric',month:'short',year:'numeric'}):'unknown date';
      document.querySelector('#restoreSummary').innerHTML='<p>This backup is dated <strong>'+esc(exported)+'</strong>.</p><p>It contains <strong>'+data.purchases.length+'</strong> purchase'+(data.purchases.length===1?'':'s')+' and <strong>'+data.observations.length+'</strong> personal price observation'+(data.observations.length===1?'':'s')+'. Restoring replaces the records currently saved on this device.</p>';
      restoreSheet.showModal();
    }catch(error){toast(error.message||'Could not read that backup.')}
    finally{event.target.value=''}
  };
  document.querySelector('#restoreReplace').onclick=async()=>{
    if(!pendingImport)return;
    restoreSheet.close();
    const ok=await confirmAction('Replace saved data?','This replaces the purchases, price notes and saved rate currently on this device.','Replace data');
    if(!ok)return;
    purchases=pendingImport.purchases;observations=pendingImport.observations;rate=pendingImport.rate||null;pendingImport=null;
    await Promise.all([put('purchases',purchases),put('observations',observations),put('rate',rate)]);
    renderHome();renderSpending();renderSettings();updateConverter();toast('Backup restored');
  };

  document.querySelector('#history').addEventListener('click',async event=>{
    const button=event.target.closest('[data-del]');if(!button)return;
    event.preventDefault();event.stopPropagation();event.stopImmediatePropagation();
    const id=button.dataset.del,record=purchases.find(p=>String(p.id)===String(id));if(!record)return;
    if(!await confirmAction('Delete this purchase?','“'+record.item+'” will be removed from this device. You can only recover it from a backup.','Delete'))return;
    purchases=purchases.filter(p=>String(p.id)!==String(id));
    await put('purchases',purchases);renderSpending();renderHome();toast('Purchase deleted');
  },true);
})();
