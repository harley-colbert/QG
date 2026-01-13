# headers.py

# Define the header data with labels for each category
header_data = {
    "Quote Information": [
        "Quote Number",
        "Quote Due Date"
    ],
    "System Name": [
        "System Name"
    ],
    "Customer Contact Information": [
        "Company Name",
        "Customer Contact Name",
        "Customer Contact Telephone",
        "Customer Contact Email",
        "Customer Contact Title",
        "Company Street Address",
        "Company City/State/Zip",
        "Customer Logo"

    ],
    "Alliance Contact Information": [
        "Sales Contact",
        "Sales Title",
        "Sales Cell",
        "Sales Email"

    ],
    "Previous Projects": [
        "Previous Quote"
    ],
    "Cost Sheet": [
        "Cost Sheet 1",
        "Cost Sheet Total 1"
    ],
    "System Layout": [
        "Elevation",
        "End",
        "Iso",
        "Top",
        "Title"
    ],
    "Customer Specifications": [
        "Customer Specifications 1"
    ],
    "Summary": [  # New Summary category for Final Quotes
        "Summary Description"
    ],
    "OEE Metrics": [
        "Run Time",
        "Planned Downtime",
        "Unplanned Downtime",
        "Total [Parts] Produced",
        "Nominal Cycle Time",
        "Total Scrap ([Parts])",
        "Parts",
        "OEE",
        "Capacity",
        "Total Produced",
        "Performance",
        "Quality",
        "Availability"
    ],
    "Project Milestones": [
        "Customer Kickoff",
        "Design Acceptance",
        "Build Start",
        "Commissioning Start",
        "FAT Start",
        "Delivery"
    ],
    "Customer Parts Due": [
        "Parts Due at time of PO Description",
        "Parts Due at Build Start Description",
    ],
    "Shipping Information": [
        "Shipping Terms"
    ]
}



SPELLCHECK_CATEGORIES = [
    "System Name",
    "System Description",
    "Zone Functions",
    "System Options",
    "Project Risks",
    "Customer Parts Due"
]

# Define the key data with corresponding keys for each label
key_data = {
    "Quote Information": [
        "data.quoteNumber",
        "data.proposalDate"
    ],
    "System Name": [
        "data.systemName"
    ],
    "Customer Contact Information": [
        "data.customercontact.companyname",
        "data.customercontact.name",
        "data.customercontact.telephone",        
        "data.customercontact.email",
        "data.customercontact.title",
        "data.customercontact.address",
        "data.customercontact.address2",
        "data.customercontact.logo"

    ],
    "Alliance Contact Information": [
        "data.alliancecontact.name",
        "data.alliancecontact.title",
        "data.alliancecontact.cell",
        "data.alliancecontact.email"

    ],
    "Previous Projects": [
        "data.previousProject.quote"
    ],
    "Cost Sheet": [
        "data.costSheet.link.1",
        "data.costSheet.total.1"
    ],
    "System Layout": [
        "data.systemLayout.elevation",
        "data.systemLayout.end",
        "data.systemLayout.iso",
        "data.systemLayout.top",
        "data.systemLayout.title"
    ],
    "Customer Specifications": [
        "data.customerspecifications.1"
    ],
    "System Description": [
        "data.systemDesc.name.1",
        "data.systemDesc.description.1"
    ],
    "OEE Metrics": [
        "data.oee.runtime",
        "data.oee.planneddowntime",
        "data.oee.unplanneddowntime",
        "data.oee.total_parts_produced",
        "data.oee.nominalcycletime",
        "data.oee.totalscrap",
        "data.oee.parts",
        "data.oee.oee",
        "data.oee.capacity",
        "data.oee.totalproduced",
        "data.oee.performance",
        "data.oee.quality",
        "data.oee.availability"
    ],
    "Project Milestones": [
        "data.projectMilestones.customerKickoff",
        "data.projectMilestones.designAcceptance",
        "data.projectMilestones.buildStart",
        "data.projectMilestones.commissioningStart",
        "data.projectMilestones.fatStart",
        "data.projectMilestones.delivery"
    ],
    "Shipping Information": [
        "data.shipping.incoterms"
    ]

}

# Define which categories are visible for each quote type
budgetary_categories = [
    "Quote Information",
    "System Name",
    "Customer Contact Information",
    "Alliance Contact Information",
    "Previous Projects",
    "Customer Specifications",
    "Cost Sheet",
    "System Layout",
]

final_categories = [
    "Quote Information",
    "System Name",
    "Customer Contact Information",
    "Alliance Contact Information",
    "Previous Projects",
    "Customer Specifications",
    "Cost Sheet",
    "System Layout",
    "OEE Metrics",
    "Project Milestones",
    "Shipping Information",
    "Installation Information"  # Summary category added for Final Quotes
]

# Define all categories in the desired order
all_categories_order = [
    "Quote Information",
    "System Name",
    "Customer Contact Information",
    "Alliance Contact Information",
    "Previous Projects",
    "Customer Specifications",
    "Cost Sheet",
    "System Layout",
    "OEE Metrics",
    "Project Milestones",
    "Shipping Information",
    "Installation Information"

]

optional_categories = [
    "Previous Projects",
    "Customer Specifications",
    "System Options",
    "Installation Information"

]

# Define standard Incoterms
incoterms_list = [
    "EXW - Ex Works",
    "FCA - Free Carrier",
    "FAS - Free Alongside Ship",
    "FOB - Free on Board",
    "CFR - Cost and Freight",
    "CIF - Cost, Insurance and Freight",
    "CPT - Carriage Paid To",
    "CIP - Carriage and Insurance Paid To",
    "DAP - Delivered at Place",
    "DPU - Delivered at Place Unloaded",
    "DDP - Delivered Duty Paid"
]

# Define options for "Weeks after PO", from 0 to 52
weeks_after_po_options = [f"Week {i}" for i in range(0, 75)]  # 0 to 75 weeks

categories_with_add_button = [
    "Customer Specifications",
    "System Description",
    "System Options",
    "Project Risks"
]

spellcheck_categories = [
    "System Name",
    "Summary",
    "System Description",
    "Zone Functions",
    "System Options",
    "Project Risks"
]


file_browse_fields = {
    "System Layout": ["data.systemLayout.elevation", "data.systemLayout.end", "data.systemLayout.iso", "data.systemLayout.top","data.systemLayout.title"],
    "Customer Contact Information": ["data.customercontact.logo"],
    "Cost Sheet": ["data.costSheet.link"],
    "Previous Projects": ["data.previousProject.quote"],
    "Customer Specifications": ["data.customerSpecifications.cr"],
}