window.initPHAddressCascadeAPI = function(config) {
  const regionSel = document.getElementById(config.region);
  const provinceSel = document.getElementById(config.province);
  const citymunSel = document.getElementById(config.citymun);
  const barangaySel = document.getElementById(config.barangay);

  async function fetchJSON(url, params = {}) {
    const query = new URLSearchParams(params).toString();
    const fullUrl = query ? `${url}?${query}` : url;
    const res = await fetch(fullUrl);
    if (!res.ok) throw new Error(`Failed to fetch ${fullUrl}`);
    return res.json();
  }

  function clearSelect(sel, placeholder = 'Select') {
    sel.innerHTML = `<option value="" disabled selected>${placeholder}</option>`;
  }

  async function populateRegions() {
    clearSelect(regionSel, 'Select Region');
    try {
      const regions = await fetchJSON('/api/regions/');
      regions.forEach(region => {
        const opt = document.createElement('option');
        opt.value = region.psgc_code || region.psgc_id || region.id || region.code || region.regCode;
        opt.textContent = region.name || region.regDesc;
        regionSel.appendChild(opt);
      });
    } catch (e) {
      console.error('Error loading regions:', e);
    }
  }

  async function onRegionChange() {
    const regionId = regionSel.value;
    if (!regionId) return;

    clearSelect(provinceSel, 'Select Province');
    clearSelect(citymunSel, 'Select City/Municipality');
    clearSelect(barangaySel, 'Select Barangay');
    provinceSel.disabled = false;
    citymunSel.disabled = false;

    try {
      const provinces = await fetchJSON('/api/provinces/', { region_id: regionId });

      if (provinces.length === 0 || regionId === "0400000000") {
        // NCR or similar region with no provinces
        provinceSel.disabled = true;
        provinceSel.innerHTML = '<option value="" disabled selected>No Province</option>';
        
        const cities = await fetchJSON('/api/cities/', { region_id: regionId });
        clearSelect(citymunSel, 'Select City/Municipality');
        cities.forEach(city => {
          const opt = document.createElement('option');
          opt.value = city.psgc_id || city.id || city.code || city.citymunCode;
          opt.textContent = city.name || city.citymunDesc;
          citymunSel.appendChild(opt);
        });
      } else {
        // Normal provinces
        provinceSel.disabled = false;
        provinces.forEach(province => {
          const opt = document.createElement('option');
          opt.value = province.psgc_id || province.id || province.code || province.provCode;
          opt.textContent = province.name || province.provDesc;
          provinceSel.appendChild(opt);
        });
      }
    } catch (e) {
      console.error('Error loading provinces or cities:', e);
    }
  }

  async function onProvinceChange() {
    const provinceId = provinceSel.value;
    if (!provinceId) return;

    clearSelect(citymunSel, 'Select City/Municipality');
    clearSelect(barangaySel, 'Select Barangay');

    try {
      const cities = await fetchJSON('/api/cities/', { province_id: provinceId });
      citymunSel.disabled = false;
      cities.forEach(city => {
        const opt = document.createElement('option');
        opt.value = city.psgc_id || city.id || city.code || city.citymunCode;
        opt.textContent = city.name || city.citymunDesc;
        citymunSel.appendChild(opt);
      });
    } catch (e) {
      console.error('Error loading cities:', e);
    }
  }

  async function onCityMunChange() {
    const cityId = citymunSel.value;
    if (!cityId) return;

    clearSelect(barangaySel, 'Select Barangay');

    try {
      const barangays = await fetchJSON('/api/barangays/', { city_id: cityId });
      barangaySel.disabled = false;
      barangays.forEach(brgy => {
        const opt = document.createElement('option');
        opt.value = brgy.psgc_id || brgy.id || brgy.code || brgy.brgyCode;
        opt.textContent = brgy.name || brgy.brgyDesc;
        barangaySel.appendChild(opt);
      });
    } catch (e) {
      console.error('Error loading barangays:', e);
    }
  }

  regionSel.addEventListener('change', onRegionChange);
  provinceSel.addEventListener('change', onProvinceChange);
  citymunSel.addEventListener('change', onCityMunChange);

  populateRegions();
}
