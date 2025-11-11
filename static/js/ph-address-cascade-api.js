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

  // Local static JSON fallback (served by Django staticfiles)
  async function fetchStatic(filename) {
    const url = `/static/ecom/${filename}`;
    const res = await fetch(url);
    if (!res.ok) throw new Error(`Failed to fetch static ${url}`);
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
      // Notify that regions are loaded
      regionSel.dispatchEvent(new CustomEvent('ph:regionsLoaded', { detail: { regions } }));
    } catch (e) {
      // Fallback to static dataset (file), then hardcoded list
      try {
        const regionData = await fetchStatic('refregion.json');
        const regions = regionData.RECORDS || regionData;
        regions.forEach(region => {
          const opt = document.createElement('option');
          opt.value = region.regCode;
          opt.textContent = region.regDesc;
          regionSel.appendChild(opt);
        });
        regionSel.dispatchEvent(new CustomEvent('ph:regionsLoaded', { detail: { regions } }));
      } catch (err) {
        // Hardcoded minimal region list to ensure UI remains usable
        const HARD_REGIONS = [
          { regCode: '01', regDesc: 'Ilocos Region' },
          { regCode: '02', regDesc: 'Cagayan Valley' },
          { regCode: '03', regDesc: 'Central Luzon' },
          { regCode: '04', regDesc: 'CALABARZON' },
          { regCode: '05', regDesc: 'Bicol Region' },
          { regCode: '06', regDesc: 'Western Visayas' },
          { regCode: '07', regDesc: 'Central Visayas' },
          { regCode: '08', regDesc: 'Eastern Visayas' },
          { regCode: '09', regDesc: 'Zamboanga Peninsula' },
          { regCode: '10', regDesc: 'Northern Mindanao' },
          { regCode: '11', regDesc: 'Davao Region' },
          { regCode: '12', regDesc: 'SOCCSKSARGEN' },
          { regCode: '13', regDesc: 'National Capital Region' },
          { regCode: '14', regDesc: 'Cordillera Administrative Region' },
          { regCode: '15', regDesc: 'Bangsamoro Autonomous Region in Muslim Mindanao' },
          { regCode: '16', regDesc: 'Caraga' },
          { regCode: '17', regDesc: 'MIMAROPA' }
        ];
        HARD_REGIONS.forEach(region => {
          const opt = document.createElement('option');
          opt.value = region.regCode;
          opt.textContent = region.regDesc;
          regionSel.appendChild(opt);
        });
        regionSel.dispatchEvent(new CustomEvent('ph:regionsLoaded', { detail: { regions: HARD_REGIONS } }));
      }
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
        // Notify that cities list is loaded for NCR
        citymunSel.dispatchEvent(new CustomEvent('ph:citiesLoaded', { detail: { cities } }));
      } else {
        // Normal provinces
        provinceSel.disabled = false;
        provinces.forEach(province => {
          const opt = document.createElement('option');
          opt.value = province.psgc_id || province.id || province.code || province.provCode;
          opt.textContent = province.name || province.provDesc;
          provinceSel.appendChild(opt);
        });
        // Notify that provinces are loaded
        provinceSel.dispatchEvent(new CustomEvent('ph:provincesLoaded', { detail: { provinces } }));
      }
      // Notify region change
      regionSel.dispatchEvent(new CustomEvent('ph:regionChanged', { detail: { regionId } }));
    } catch (e) {
      // Fallback using static datasets
      try {
        const provincesData = await fetchStatic('refprovince.json');
        const allProvinces = provincesData.RECORDS || provincesData;

        // Determine if this region has provinces (e.g., NCR has none). Static regCode may be short (e.g., '13')
        const provinces = allProvinces.filter(p => {
          // Match either exact or prefix when regionId is PSGC like '130000000'
          const reg = String(p.regCode || '').trim();
          return regionId === reg || String(regionId).startsWith(reg);
        });

        if (provinces.length === 0) {
          provinceSel.disabled = true;
          provinceSel.innerHTML = '<option value="" disabled selected>No Province</option>';
          // Load cities by region for NCR-like regions
          const citiesData = await fetchStatic('refcitymun.json');
          const allCities = citiesData.RECORDS || citiesData;
          const cities = allCities.filter(c => {
            const reg = String(c.regCode || '').trim();
            return regionId === reg || String(regionId).startsWith(reg);
          });
          clearSelect(citymunSel, 'Select City/Municipality');
          cities.forEach(city => {
            const opt = document.createElement('option');
            opt.value = city.citymunCode;
            opt.textContent = city.citymunDesc || city.citymun_name || city.name;
            citymunSel.appendChild(opt);
          });
          citymunSel.dispatchEvent(new CustomEvent('ph:citiesLoaded', { detail: { cities } }));
        } else {
          provinceSel.disabled = false;
          provinces.forEach(province => {
            const opt = document.createElement('option');
            opt.value = province.provCode;
            opt.textContent = province.provDesc || province.prov_name || province.name;
            provinceSel.appendChild(opt);
          });
          provinceSel.dispatchEvent(new CustomEvent('ph:provincesLoaded', { detail: { provinces } }));
        }
        regionSel.dispatchEvent(new CustomEvent('ph:regionChanged', { detail: { regionId } }));
      } catch (err) {
        console.warn('Address provinces/cities static fallback failed:', err);
      }
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
      // Notify that cities are loaded
      citymunSel.dispatchEvent(new CustomEvent('ph:citiesLoaded', { detail: { cities } }));
      provinceSel.dispatchEvent(new CustomEvent('ph:provinceChanged', { detail: { provinceId } }));
    } catch (e) {
      // Static fallback for cities
      try {
        const citiesData = await fetchStatic('refcitymun.json');
        const allCities = citiesData.RECORDS || citiesData;
        const cities = allCities.filter(c => String(c.provCode || '').trim() === String(provinceId).trim());
        citymunSel.disabled = false;
        cities.forEach(city => {
          const opt = document.createElement('option');
          opt.value = city.citymunCode;
          opt.textContent = city.citymunDesc || city.citymun_name || city.name;
          citymunSel.appendChild(opt);
        });
        citymunSel.dispatchEvent(new CustomEvent('ph:citiesLoaded', { detail: { cities } }));
        provinceSel.dispatchEvent(new CustomEvent('ph:provinceChanged', { detail: { provinceId } }));
      } catch (err) {
        console.warn('Address cities static fallback failed:', err);
      }
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
      // Notify that barangays are loaded
      barangaySel.dispatchEvent(new CustomEvent('ph:barangaysLoaded', { detail: { barangays } }));
      citymunSel.dispatchEvent(new CustomEvent('ph:cityChanged', { detail: { cityId } }));
    } catch (e) {
      // Static fallback for barangays
      try {
        const brgyData = await fetchStatic('refbrgy.json');
        const allBrgys = brgyData.RECORDS || brgyData;
        const barangays = allBrgys.filter(b => String(b.citymunCode || '').trim() === String(cityId).trim());
        barangaySel.disabled = false;
        barangays.forEach(brgy => {
          const opt = document.createElement('option');
          opt.value = brgy.brgyCode;
          opt.textContent = brgy.brgyDesc || brgy.brgy_name || brgy.name;
          barangaySel.appendChild(opt);
        });
        barangaySel.dispatchEvent(new CustomEvent('ph:barangaysLoaded', { detail: { barangays } }));
        citymunSel.dispatchEvent(new CustomEvent('ph:cityChanged', { detail: { cityId } }));
      } catch (err) {
        console.error('Error loading barangays (static fallback failed):', err);
      }
    }
  }

  regionSel.addEventListener('change', onRegionChange);
  provinceSel.addEventListener('change', onProvinceChange);
  citymunSel.addEventListener('change', onCityMunChange);
  
  // Sync visible barangay select with hidden form field
  barangaySel.addEventListener('change', function() {
    const hiddenBarangayField = document.querySelector('input[name="barangay"]');
    if (hiddenBarangayField) {
      hiddenBarangayField.value = this.value;
    }
  });

  populateRegions();
}
