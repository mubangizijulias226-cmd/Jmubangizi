// Swap this sample DATA object with real exported UNSDCF regional data.
window.DATA = {
  countries: [
    { country: 'Ethiopia', sub_region: 'Eastern Africa', cf_cycle: '2022–2026' },
    { country: 'Kenya', sub_region: 'Eastern Africa', cf_cycle: '2023–2027' },
    { country: 'Nigeria', sub_region: 'Western Africa', cf_cycle: '2022–2026' },
    { country: 'Senegal', sub_region: 'Western Africa', cf_cycle: '2022–2026' },
    { country: 'DRC', sub_region: 'Central Africa', cf_cycle: '2023–2027' },
    { country: 'Morocco', sub_region: 'Northern Africa', cf_cycle: '2022–2026' },
    { country: 'South Africa', sub_region: 'Southern Africa', cf_cycle: '2022–2026' },
    { country: 'Uganda', sub_region: 'Eastern Africa', cf_cycle: '2023–2027' },
    { country: 'Ghana', sub_region: 'Western Africa', cf_cycle: '2022–2026' },
    { country: 'Mozambique', sub_region: 'Southern Africa', cf_cycle: '2023–2027' }
  ],
  portfolio: [
    { country:'Ethiopia', sub_region:'Eastern Africa', required_resources:120, available_resources:95, expenditure:88, thematic_pillar:'People', agency_name:'UNICEF', joint_programme_count:4, active_outputs:34, cancelled_outputs:2, suspended_outputs:1 },
    { country:'Kenya', sub_region:'Eastern Africa', required_resources:110, available_resources:104, expenditure:91, thematic_pillar:'Prosperity', agency_name:'UNDP', joint_programme_count:6, active_outputs:30, cancelled_outputs:1, suspended_outputs:0 },
    { country:'Nigeria', sub_region:'Western Africa', required_resources:200, available_resources:140, expenditure:90, thematic_pillar:'Peace', agency_name:'UNFPA', joint_programme_count:5, active_outputs:40, cancelled_outputs:4, suspended_outputs:2 },
    { country:'Senegal', sub_region:'Western Africa', required_resources:70, available_resources:62, expenditure:58, thematic_pillar:'Partnership', agency_name:'WHO', joint_programme_count:3, active_outputs:18, cancelled_outputs:0, suspended_outputs:1 },
    { country:'DRC', sub_region:'Central Africa', required_resources:150, available_resources:82, expenditure:51, thematic_pillar:'People', agency_name:'WFP', joint_programme_count:4, active_outputs:27, cancelled_outputs:5, suspended_outputs:3 },
    { country:'Morocco', sub_region:'Northern Africa', required_resources:80, available_resources:76, expenditure:73, thematic_pillar:'Planet', agency_name:'FAO', joint_programme_count:2, active_outputs:16, cancelled_outputs:0, suspended_outputs:0 },
    { country:'South Africa', sub_region:'Southern Africa', required_resources:140, available_resources:130, expenditure:122, thematic_pillar:'Prosperity', agency_name:'UN Women', joint_programme_count:5, active_outputs:29, cancelled_outputs:1, suspended_outputs:1 },
    { country:'Uganda', sub_region:'Eastern Africa', required_resources:95, available_resources:67, expenditure:54, thematic_pillar:'Peace', agency_name:'UNHCR', joint_programme_count:3, active_outputs:22, cancelled_outputs:3, suspended_outputs:2 },
    { country:'Ghana', sub_region:'Western Africa', required_resources:90, available_resources:85, expenditure:74, thematic_pillar:'Partnership', agency_name:'UNDP', joint_programme_count:4, active_outputs:21, cancelled_outputs:0, suspended_outputs:1 },
    { country:'Mozambique', sub_region:'Southern Africa', required_resources:100, available_resources:60, expenditure:48, thematic_pillar:'Planet', agency_name:'UNICEF', joint_programme_count:3, active_outputs:20, cancelled_outputs:2, suspended_outputs:3 }
  ],
  cfAnalysis: [
    {sub_output_id:'SO1',country:'Ethiopia',gender_marker:'GM2',lnob_group:'Refugees',sdg_goal:2,geographic_level:'subnational',un_function_type:'Capacity Development',output_status:'active'},
    {sub_output_id:'SO2',country:'Kenya',gender_marker:'GM3',lnob_group:'Youth',sdg_goal:5,geographic_level:'subnational',un_function_type:'Technical Assistance',output_status:'active'},
    {sub_output_id:'SO3',country:'Nigeria',gender_marker:'GM0',lnob_group:'IDPs',sdg_goal:16,geographic_level:'national',un_function_type:'Direct Service Delivery',output_status:'active'},
    {sub_output_id:'SO4',country:'Senegal',gender_marker:'GM1',lnob_group:'Persons with disabilities',sdg_goal:4,geographic_level:'subnational',un_function_type:'Advocacy',output_status:'active'},
    {sub_output_id:'SO5',country:'DRC',gender_marker:'GM0',lnob_group:'Women-headed households',sdg_goal:1,geographic_level:'national',un_function_type:'Normative',output_status:'active'},
    {sub_output_id:'SO6',country:'Morocco',gender_marker:'GM2',lnob_group:'Migrants',sdg_goal:8,geographic_level:'subnational',un_function_type:'Capacity Development',output_status:'active'},
    {sub_output_id:'SO7',country:'South Africa',gender_marker:'GM3',lnob_group:'Adolescents',sdg_goal:10,geographic_level:'subnational',un_function_type:'Technical Assistance',output_status:'active'},
    {sub_output_id:'SO8',country:'Uganda',gender_marker:'GM1',lnob_group:'Refugees',sdg_goal:3,geographic_level:'national',un_function_type:'Direct Service Delivery',output_status:'active'},
    {sub_output_id:'SO9',country:'Ghana',gender_marker:'GM2',lnob_group:'Rural poor',sdg_goal:9,geographic_level:'subnational',un_function_type:'Advocacy',output_status:'active'},
    {sub_output_id:'SO10',country:'Mozambique',gender_marker:'GM0',lnob_group:'Coastal communities',sdg_goal:13,geographic_level:'national',un_function_type:'Normative',output_status:'active'}
  ],
  rco:[
    {staff_id:'S1',country:'Ethiopia',gender:'F',functional_area:'Data Management',post_status:'filled',unct_agency:'UNDP',cf_signatory:'Y',physical_presence:'Y'},
    {staff_id:'S2',country:'Kenya',gender:'M',functional_area:'Programme',post_status:'vacant',unct_agency:'UNICEF',cf_signatory:'Y',physical_presence:'Y'},
    {staff_id:'S3',country:'Nigeria',gender:'F',functional_area:'M&E',post_status:'filled',unct_agency:'UNESCO',cf_signatory:'Pending',physical_presence:'N'},
    {staff_id:'S4',country:'DRC',gender:'F',functional_area:'Admin',post_status:'vacant',unct_agency:'WHO',cf_signatory:'N',physical_presence:'Y'}
  ],
  cca:[
    {country:'Ethiopia',cca_last_updated:'2025-11-01',cca_type:'full CCA',entry_points_documented:'Y',challenges_documented:'Y',foresight_section:'Y',cf_cycle_start_year:2022},
    {country:'Kenya',cca_last_updated:'2023-01-15',cca_type:'light update',entry_points_documented:'Y',challenges_documented:'Y',foresight_section:'N',cf_cycle_start_year:2023},
    {country:'Nigeria',cca_last_updated:'',cca_type:'',entry_points_documented:'N',challenges_documented:'N',foresight_section:'N',cf_cycle_start_year:2022}
  ],
  water:[
    {country:'Ethiopia',output_id:'W1',output_title:'Climate-smart irrigation',water_tag:'Y',water_framing:'cross_cutting',thematic_linkage:['Climate Resilience','Food Systems'],food_systems_link:'Y'},
    {country:'Nigeria',output_id:'W2',output_title:'Urban WASH',water_tag:'Y',water_framing:'sdg6_only',thematic_linkage:['WASH'],food_systems_link:'N'},
    {country:'Morocco',output_id:'W3',output_title:'Water reuse policy',water_tag:'Y',water_framing:'cross_cutting',thematic_linkage:['Health','Climate Resilience'],food_systems_link:'N'}
  ],
  experts:[
    {expert_name:'Amina Bekele',country:'Ethiopia',skills:['Data','M&E'],languages:['English','Amharic'],availability:'both',contact_email:'amina@example.org',bio:'Results monitoring specialist.'},
    {expert_name:'Kwame Mensah',country:'Ghana',skills:['AI','Reporting'],languages:['English','French'],availability:'remote',contact_email:'kwame@example.org',bio:'AI for development practitioner.'}
  ],
  results:[
    {indicator_id:'I1',country:'Ethiopia',indicator_title:'Maternal mortality reduction',sdg_goal:3,thematic_pillar:'People',status:'on_track',baseline_value:420,baseline_year:2020,target_value:300,target_year:2026,latest_result:350,result_year:2025,reporting_year:2025,flag:'none'},
    {indicator_id:'I2',country:'Nigeria',indicator_title:'Out-of-school children',sdg_goal:4,thematic_pillar:'People',status:'off_track',baseline_value:12000000,baseline_year:2020,target_value:8000000,target_year:2026,latest_result:11500000,result_year:2025,reporting_year:2025,flag:'none'},
    {indicator_id:'I3',country:'DRC',indicator_title:'Access to clean water',sdg_goal:6,thematic_pillar:'Planet',status:'unknown',baseline_value:null,baseline_year:null,target_value:null,target_year:2026,latest_result:null,result_year:null,reporting_year:2025,flag:'missing_target'},
    {indicator_id:'I4',country:'Kenya',indicator_title:'Digital inclusion',sdg_goal:9,thematic_pillar:'Prosperity',status:'on_track',baseline_value:45,baseline_year:2021,target_value:70,target_year:2027,latest_result:60,result_year:2028,reporting_year:2026,flag:'future_dated'}
  ]
};
