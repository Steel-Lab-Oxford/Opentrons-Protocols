from opentrons import protocol_api
metadata = {
    'protocolName': 'Vacuum miniprep 24 samples',
    'description': 'Miniprep 24 samples using 3D printed vacuum manifold. Start with resuspended cells in 2ml tubes.',
    'author': 'JATD'
    }

requirements = {
    "robotType": "Flex",
    "apiLevel": "2.23",
}

def run(protocol: protocol_api.ProtocolContext):
    # Load labware
    tips1 = protocol.load_labware("opentrons_flex_96_tiprack_50ul", location = "A2") 
    tips2 = protocol.load_labware("opentrons_flex_96_tiprack_50ul", location = "C1")
    trash = protocol.load_trash_bin(location="A3")
    left_pipette = protocol.load_instrument(
        "flex_1channel_50",
        mount="left",
        tip_racks=[tips1,tips2]
    )

    # define reagents and labware 
    cells = protocol.load_labware("jd_24_tuberack_1.5ml", "B2")
    VacManifold = protocol.load_labware('jdvacuum_24_tuberack_500ul', 'B3')
    buffers = protocol.load_labware('jd_6_falconrack_50ml', 'C2')
    elution_tubes = protocol.load_labware('jd_24_tuberack_1.5ml', 'C3')

    ### Process each column: Lyse then Neutralize before moving to next column ###
    # Process in batches of 4 wells (one column at a time)
    for col in range(6):  # 6 columns (A-F)
        column_wells = [cells.wells()[col * 4 + row] for row in range(4)]  # Get 4 wells in column
        
        protocol.comment(f"Processing column {col + 1} - wells {[well.well_name for well in column_wells]}")
        
        ### 1. Lyse cells by adding 250ul Lysis buffer ###
        # Add lysis buffer to all 4 wells in column
        for well in column_wells:
            left_pipette.pick_up_tip()
            left_pipette.transfer(
                250,
                buffers["A1"].bottom(3) , 
                well.top(0),
                new_tip="never",
            )
            left_pipette.mix(3, 45, well)
            left_pipette.drop_tip()

        protocol.comment(f"Neutralizing column {col + 1}")

        ### 2. Neutralize by adding 350ul Neutralisation buffer ###
        for well in column_wells:
            left_pipette.pick_up_tip()
            left_pipette.transfer(
                350,
                buffers["A2"].bottom(3) , 
                well.top(0),
                new_tip="never", 
            )
            left_pipette.mix(3, 45, well)
            left_pipette.drop_tip()

    ### Pause for user to spin down samples and load into vacuum manifold ###
    protocol.pause("Please spin down samples and load into vacuum manifold. Click Resume when ready.")

    ### 3. Bind DNA to the column ###
    left_pipette.pick_up_tip()
    for i in range(24):
        left_pipette.transfer(
            500,
            buffers["A3"].bottom(3) , 
            VacManifold.wells()[i].top(1),
            new_tip="never",
        )
    for i in range(24):
        left_pipette.transfer(
            500,
            buffers["A3"].bottom(3) , 
            VacManifold.wells()[i].top(1),
            new_tip="never",
        )
    left_pipette.drop_tip()
    protocol.pause("Please transfer samples to elution tubes. Click Resume when ready.")

    left_pipette.pick_up_tip()
    for i in range(24):
        left_pipette.transfer(
            50,
            buffers["B1"].bottom(3) , 
            elution_tubes.wells()[i].top(),
            new_tip="never"
        )
    left_pipette.drop_tip()
    # End of protocol
    protocol.comment("Protocol complete, spin down samples and store elutions at -20C")







    