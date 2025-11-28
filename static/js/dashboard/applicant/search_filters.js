document.addEventListener('DOMContentLoaded', function(){
    const toggleBtn = document.getElementById('toggleFiltersBtn');
    const panel = document.getElementById('filtersPanel');
    if(!toggleBtn || !panel) return;

    function setState(open){
        if(open){
            panel.classList.add('open');
            panel.classList.remove('collapsed');
            panel.setAttribute('aria-hidden','false');
            toggleBtn.classList.add('active');
            toggleBtn.setAttribute('aria-expanded','true');
            // use measured height for smooth animation
            panel.style.maxHeight = panel.scrollHeight + 'px';
        } else {
            panel.classList.remove('open');
            panel.classList.add('collapsed');
            panel.setAttribute('aria-hidden','true');
            toggleBtn.classList.remove('active');
            toggleBtn.setAttribute('aria-expanded','false');
            panel.style.maxHeight = '0px';
        }
    }

    // initialize based on presence of selected filters (if any)
    const anyFilterSet = Array.from(panel.querySelectorAll('select, input')).some(el => {
        try { return el.value && el.value !== ''; } catch(e){ return false; }
    });
    setState(!!anyFilterSet);

    toggleBtn.addEventListener('click', function(e){
        e.preventDefault();
        e.stopPropagation();
        const isOpen = panel.classList.contains('open');
        setState(!isOpen);
    });

    // close if clicked outside the panel & toggle
    document.addEventListener('click', function(e){
        if(!panel.classList.contains('open')) return;
        const target = e.target;
        if(!panel.contains(target) && !toggleBtn.contains(target)){
            setState(false);
        }
    });
});