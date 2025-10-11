// ph-address-cascade.js
// Dynamically populates Region, Province, City/Municipality, and Barangay dropdowns using PH address JSON files

window.initPHAddressCascade = function(config) {
  const regionSel = document.getElementById(config.region);
  const provinceSel = document.getElementById(config.province);
  const citymunSel = document.getElementById(config.citymun);
  const barangaySel = document.getElementById(config.barangay);
  const staticPath = config.staticPath;

  let regions = [], provinces = [], citymuns = [], barangays = [];

  // Helper: fetch and cache JSON
  async function fetchJSON(filename) {
    const res = await fetch(staticPath + filename);
    return res.json();
  }

  // Load all JSON files
  Promise.all([
    fetchJSON('refregion.json'),
    fetchJSON('refprovince.json'),
    fetchJSON('refcitymun.json'),
    fetchJSON('refbrgy.json')
  ]).then(function([regionData, provinceData, citymunData, brgyData]) {
    regions = regionData.RECORDS || regionData;
    provinces = provinceData.RECORDS || provinceData;
    citymuns = citymunData.RECORDS || citymunData;
    barangays = brgyData.RECORDS || brgyData;
    populateRegions();
  });

  function clearSelect(sel) {
    sel.innerHTML = '<option value="" disabled selected>Select</option>';
  }

  function populateRegions() {
    clearSelect(regionSel);
    regionSel.innerHTML = '<option value="" disabled selected>Select Region</option>';
    regions.forEach(function(region) {
      const opt = document.createElement('option');
      opt.value = region.regCode;
      opt.textContent = region.regDesc;
      regionSel.appendChild(opt);
    });
    regionSel.onchange = onRegionChange;
    provinceSel.onchange = onProvinceChange;
    citymunSel.onchange = onCityMunChange;
  }

  function onRegionChange() {
    clearSelect(provinceSel);
    clearSelect(citymunSel);
    clearSelect(barangaySel);
    provinceSel.innerHTML = '<option value="" disabled selected>Select Province</option>';
    const regCode = regionSel.value;
    provinces.filter(p => p.regCode === regCode).forEach(function(province) {
      const opt = document.createElement('option');
      opt.value = province.provCode;
      opt.textContent = province.provDesc;
      provinceSel.appendChild(opt);
    });
  }

  function onProvinceChange() {
    clearSelect(citymunSel);
    clearSelect(barangaySel);
    citymunSel.innerHTML = '<option value="" disabled selected>Select City/Municipality</option>';
    const provCode = provinceSel.value;
    citymuns.filter(c => c.provCode === provCode).forEach(function(citymun) {
      const opt = document.createElement('option');
      opt.value = citymun.citymunCode;
      opt.textContent = citymun.citymunDesc;
      citymunSel.appendChild(opt);
    });
  }

  function onCityMunChange() {
    clearSelect(barangaySel);
    barangaySel.innerHTML = '<option value="" disabled selected>Select Barangay</option>';
    const citymunCode = citymunSel.value;
    barangays.filter(b => b.citymunCode === citymunCode).forEach(function(brgy) {
      const opt = document.createElement('option');
      opt.value = brgy.brgyCode;
      opt.textContent = brgy.brgyDesc;
      barangaySel.appendChild(opt);
    });
  }
}
