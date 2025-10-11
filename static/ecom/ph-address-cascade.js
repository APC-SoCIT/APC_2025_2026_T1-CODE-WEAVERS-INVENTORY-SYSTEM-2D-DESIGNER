// Simple PH address cascade using backend PSGC endpoints
// Exposes window.initPHAddressCascade({ region, province, citymun, barangay })

(function() {
  function qs(id) { return document.getElementById(id); }
  function clearSelect(sel, placeholder) {
    if (!sel) return;
    sel.innerHTML = '';
    const opt = document.createElement('option');
    opt.value = '';
    opt.textContent = placeholder || 'Select';
    sel.appendChild(opt);
    sel.disabled = true;
  }
  function enableSelect(sel) { if (sel) sel.disabled = false; }
  function addOptions(sel, items, getValue, getText) {
    if (!sel || !Array.isArray(items)) return;
    items.forEach(item => {
      const opt = document.createElement('option');
      opt.value = getValue(item);
      opt.textContent = getText(item);
      sel.appendChild(opt);
    });
  }

  async function fetchJSON(url) {
    const res = await fetch(url, { credentials: 'same-origin' });
    if (!res.ok) throw new Error('Network error ' + res.status);
    return res.json();
  }

  function init(config) {
    const regionSel = qs(config.region);
    const provSel = qs(config.province);
    const citySel = qs(config.citymun);
    const brgySel = qs(config.barangay);

    clearSelect(regionSel, 'Select Region');
    clearSelect(provSel, 'Select Province');
    clearSelect(citySel, 'Select City/Municipality');
    clearSelect(brgySel, 'Select Barangay');

    // Load regions
    fetchJSON('/api/regions/')
      .then(data => {
        enableSelect(regionSel);
        addOptions(regionSel, data, r => r.code, r => r.name);
      })
      .catch(() => {
        // Fallback: try static region JSON if available
        if (config.staticPath) {
          fetchJSON(config.staticPath + 'refregion.json').then(json => {
            enableSelect(regionSel);
            addOptions(regionSel, json, r => r.regCode, r => r.regDesc);
          }).catch(() => {});
        }
      });

    // Region change -> provinces or cities (for NCR-like regions)
    regionSel && regionSel.addEventListener('change', async function() {
      const regionId = regionSel.value;
      clearSelect(provSel, 'Select Province');
      clearSelect(citySel, 'Select City/Municipality');
      clearSelect(brgySel, 'Select Barangay');
      if (!regionId) return;

      // Try provinces under region
      try {
        const provinces = await fetchJSON('/api/provinces/?region_id=' + encodeURIComponent(regionId));
        if (Array.isArray(provinces) && provinces.length > 0) {
          enableSelect(provSel);
          addOptions(provSel, provinces, p => p.code, p => p.name);
        } else {
          // No provinces: populate cities directly under region
          const cities = await fetchJSON('/api/cities/?region_id=' + encodeURIComponent(regionId));
          enableSelect(citySel);
          addOptions(citySel, cities, c => c.code, c => c.name);
        }
      } catch (e) {
        // Fallback: no provinces JSON locally; skip
      }
    });

    // Province change -> cities
    provSel && provSel.addEventListener('change', async function() {
      const provId = provSel.value;
      clearSelect(citySel, 'Select City/Municipality');
      clearSelect(brgySel, 'Select Barangay');
      if (!provId) return;
      try {
        const cities = await fetchJSON('/api/cities/?province_id=' + encodeURIComponent(provId));
        enableSelect(citySel);
        addOptions(citySel, cities, c => c.code, c => c.name);
      } catch (e) {}
    });

    // City change -> barangays
    citySel && citySel.addEventListener('change', async function() {
      const cityId = citySel.value;
      clearSelect(brgySel, 'Select Barangay');
      if (!cityId) return;
      try {
        const barangays = await fetchJSON('/api/barangays/?city_id=' + encodeURIComponent(cityId));
        enableSelect(brgySel);
        addOptions(brgySel, barangays, b => b.code, b => b.name);
      } catch (e) {
        // Fallback: try static barangays if available
        if (config.staticPath) {
          fetchJSON(config.staticPath + 'refbrgy.json').then(json => {
            // Filter by cityId when structure matches
            const list = Array.isArray(json) ? json.filter(b => String(b.citymunCode) === String(cityId)) : [];
            enableSelect(brgySel);
            addOptions(brgySel, list, b => b.brgyCode, b => b.brgyDesc);
          }).catch(() => {});
        }
      }
    });
  }

  window.initPHAddressCascade = init;
})();