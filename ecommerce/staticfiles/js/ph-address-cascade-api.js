window.initPHAddressCascadeAPI = function(config) {
  const regionSel = document.getElementById(config.region);
  const provinceSel = document.getElementById(config.province);
  const citymunSel = document.getElementById(config.citymun);
  const barangaySel = document.getElementById(config.barangay);

  console.log('Initializing address cascade with elements:', {
    region: regionSel,
    province: provinceSel,
    citymun: citymunSel,
    barangay: barangaySel
  });

  async function fetchJSON(url, params = {}) {
    try {
      console.log(`Fetching data from ${url} with params:`, params);
      const query = new URLSearchParams(params).toString();
      const fullUrl = query ? `${url}?${query}` : url;
      
      const response = await fetch(fullUrl, {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
          'X-Requested-With': 'XMLHttpRequest'
        },
        credentials: 'same-origin'
      });
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status} - ${response.statusText}`);
      }
      
      const contentType = response.headers.get('content-type');
      if (!contentType || !contentType.includes('application/json')) {
        throw new Error(`Expected JSON response but got ${contentType}`);
      }
      
      const data = await response.json();
      console.log(`Received data from ${url}:`, data);
      return data;
    } catch (error) {
      console.error(`Error fetching from ${url}:`, error);
      console.error('Full error details:', {
        message: error.message,
        url: url,
        params: params
      });
      throw error;
    }
  }

  function clearSelect(sel, placeholder = 'Select') {
    if (!sel) {
      console.error('Cannot clear select: element is null');
      return;
    }
    sel.innerHTML = `<option value="" disabled selected>${placeholder}</option>`;
    console.log(`Cleared select element ${sel.id} with placeholder: ${placeholder}`);
  }

  async function populateRegions() {
    console.log('Starting to populate regions...');
    if (!regionSel) {
      console.error('Region select element not found');
      return;
    }

    clearSelect(regionSel, 'Select Region');
    try {
      const regions = await fetchJSON('/api/regions/');
      console.log('Received regions:', regions);

      if (!Array.isArray(regions)) {
        console.error('Received invalid regions data:', regions);
        return;
      }

      // Sort regions by name
      regions.sort((a, b) => (a.name || a.regDesc).localeCompare(b.name || b.regDesc));

      regions.forEach(region => {
        const opt = document.createElement('option');
        opt.value = region.psgc_code || region.regCode;
        opt.textContent = region.name || region.regDesc;
        regionSel.appendChild(opt);
        console.log(`Added region option: ${opt.textContent} (${opt.value})`);
      });

      console.log(`Successfully populated ${regions.length} regions`);
    } catch (e) {
      console.error('Error loading regions:', e);
      clearSelect(regionSel, 'Error loading regions');
    }
  }

  async function onRegionChange() {
    const regionId = regionSel.value;
    console.log('Region changed to:', regionId);
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
        cities.sort((a, b) => (a.name || a.citymunDesc).localeCompare(b.name || b.citymunDesc));
        cities.forEach(city => {
          const opt = document.createElement('option');
          opt.value = city.psgc_id || city.citymunCode;
          opt.textContent = city.name || city.citymunDesc;
          citymunSel.appendChild(opt);
        });
      } else {
        // Normal provinces
        provinceSel.disabled = false;
        provinces.sort((a, b) => (a.name || a.provDesc).localeCompare(b.name || b.provDesc));
        provinces.forEach(province => {
          const opt = document.createElement('option');
          opt.value = province.psgc_id || province.provCode;
          opt.textContent = province.name || province.provDesc;
          provinceSel.appendChild(opt);
        });
      }
    } catch (e) {
      console.error('Error loading provinces or cities:', e);
      clearSelect(provinceSel, 'Error loading provinces');
      clearSelect(citymunSel, 'Error loading cities');
    }
  }

  async function onProvinceChange() {
    const provinceId = provinceSel.value;
    console.log('Province changed to:', provinceId);
    if (!provinceId) return;

    clearSelect(citymunSel, 'Select City/Municipality');
    clearSelect(barangaySel, 'Select Barangay');

    try {
      const cities = await fetchJSON('/api/cities/', { province_id: provinceId });
      citymunSel.disabled = false;
      cities.sort((a, b) => (a.name || a.citymunDesc).localeCompare(b.name || b.citymunDesc));
      cities.forEach(city => {
        const opt = document.createElement('option');
        opt.value = city.psgc_id || city.citymunCode;
        opt.textContent = city.name || city.citymunDesc;
        citymunSel.appendChild(opt);
      });
    } catch (e) {
      console.error('Error loading cities:', e);
      clearSelect(citymunSel, 'Error loading cities');
    }
  }

  async function onCityMunChange() {
    const cityId = citymunSel.value;
    console.log('City/Municipality changed to:', cityId);
    if (!cityId) return;

    clearSelect(barangaySel, 'Select Barangay');

    try {
      const barangays = await fetchJSON('/api/barangays/', { city_id: cityId });
      barangaySel.disabled = false;
      barangays.sort((a, b) => (a.name || a.brgyDesc).localeCompare(b.name || b.brgyDesc));
      barangays.forEach(brgy => {
        const opt = document.createElement('option');
        opt.value = brgy.psgc_id || brgy.brgyCode;
        opt.textContent = brgy.name || brgy.brgyDesc;
        barangaySel.appendChild(opt);
      });
    } catch (e) {
      console.error('Error loading barangays:', e);
      clearSelect(barangaySel, 'Error loading barangays');
    }
  }

  // Add event listeners
  if (regionSel) {
    regionSel.addEventListener('change', onRegionChange);
    console.log('Added change event listener to region select');
  }
  if (provinceSel) {
    provinceSel.addEventListener('change', onProvinceChange);
    console.log('Added change event listener to province select');
  }
  if (citymunSel) {
    citymunSel.addEventListener('change', onCityMunChange);
    console.log('Added change event listener to city/municipality select');
  }

  // Initialize regions
  populateRegions();
}
