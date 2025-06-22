// ph-address-cascade-api.js
// Dynamically populates Region, Province, City/Municipality, and Barangay dropdowns using PSGC API proxy endpoints

window.initPHAddressCascadeAPI = function(config) {
  const regionSel = document.getElementById(config.region);
  const provinceSel = document.getElementById(config.province);
  const citymunSel = document.getElementById(config.citymun);
  const barangaySel = document.getElementById(config.barangay);

  // Helper: fetch JSON from API endpoint with optional params
  async function fetchJSON(url, params = {}) {
    const query = new URLSearchParams(params).toString();
    const fullUrl = query ? `${url}?${query}` : url;
    const res = await fetch(fullUrl);
    if (!res.ok) throw new Error(`Failed to fetch ${fullUrl}`);
    return res.json();
  }

  function clearSelect(sel) {
    sel.innerHTML = '<option value="" disabled selected>Select</option>';
  }

  async function populateRegions() {
    clearSelect(regionSel);
    regionSel.innerHTML = '<option value="" disabled selected>Select Region</option>';
    try {
      const regions = await fetchJSON('/api/regions/');
      regions.forEach(region => {
        const opt = document.createElement('option');
        opt.value = region.psgc_id || region.id || region.code || region.regCode;
        opt.textContent = region.name || region.regDesc;
        regionSel.appendChild(opt);
      });
    } catch (e) {
      console.error(e);
    }
  }

  async function onRegionChange() {
    clearSelect(provinceSel);
    clearSelect(citymunSel);
    clearSelect(barangaySel);
    provinceSel.innerHTML = '<option value="" disabled selected>Select Province</option>';
    const regionId = regionSel.value;
    if (!regionId) return;
    try {
      const provinces = await fetchJSON('/api/provinces/', {region_id: regionId});
      provinces.forEach(province => {
        const opt = document.createElement('option');
        opt.value = province.psgc_id || province.id || province.code || province.provCode;
        opt.textContent = province.name || province.provDesc;
        provinceSel.appendChild(opt);
      });
    } catch (e) {
      console.error(e);
    }
  }

  async function onProvinceChange() {
    clearSelect(citymunSel);
    clearSelect(barangaySel);
    citymunSel.innerHTML = '<option value="" disabled selected>Select City/Municipality</option>';
    const provinceId = provinceSel.value;
    if (!provinceId) return;
    try {
      const cities = await fetchJSON('/api/cities/', {province_id: provinceId});
      cities.forEach(city => {
        const opt = document.createElement('option');
        opt.value = city.psgc_id || city.id || city.code || city.citymunCode;
        opt.textContent = city.name || city.citymunDesc;
        citymunSel.appendChild(opt);
      });
    } catch (e) {
      console.error(e);
    }
  }

  async function onCityMunChange() {
    clearSelect(barangaySel);
    barangaySel.innerHTML = '<option value="" disabled selected>Select Barangay</option>';
    const cityId = citymunSel.value;
    if (!cityId) return;
    try {
      const barangays = await fetchJSON('/api/barangays/', {city_id: cityId});
      barangays.forEach(brgy => {
        const opt = document.createElement('option');
        opt.value = brgy.psgc_id || brgy.id || brgy.code || brgy.brgyCode;
        opt.textContent = brgy.name || brgy.brgyDesc;
        barangaySel.appendChild(opt);
      });
    } catch (e) {
      console.error(e);
    }
  }

  regionSel.addEventListener('change', onRegionChange);
  provinceSel.addEventListener('change', onProvinceChange);
  citymunSel.addEventListener('change', onCityMunChange);

  // Initialize by populating regions
  populateRegions();
};
