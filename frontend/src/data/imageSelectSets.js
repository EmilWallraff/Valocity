export const agentOptions = [
    { label: "Astra", hashcode: "41FB69C1-4189-7B37-F117-BCAF1E96F1BF" },
    { label: "Breach", hashcode: "5F8D3A7F-467B-97F3-062C-13ACF203C006" },
    { label: "Brimstone", hashcode: "9F0D8BA9-4140-B941-57D3-A7AD57C6B417" },
    { label: "Chamber", hashcode: "22697A3D-45BF-8DD7-4FEC-84A9E28C69D7" },
    { label: "Clove", hashcode: "1DBF2EDD-4729-0984-3115-DAA5EED44993" },
    { label: "Cypher", hashcode: "117ED9E3-49F3-6512-3CCF-0CADA7E3823B" },
    { label: "Deadlock", hashcode: "CC8B64C8-4B25-4FF9-6E7F-37B4DA43D235" },
    { label: "Fade", hashcode: "DADE69B4-4F5A-8528-247B-219E5A1FACD6" },
    { label: "Gekko", hashcode: "E370FA57-4757-3604-3648-499E1F642D3F" },
    { label: "Harbor", hashcode: "95B78ED7-4637-86D9-7E41-71BA8C293152" },
    { label: "Iso", hashcode: "0E38B510-41A8-5780-5E8F-568B2A4F2D6C" },
    { label: "Jett", hashcode: "ADD6443A-41BD-E414-F6AD-E58D267F4E95" },
    { label: "KAY/O", hashcode: "601DBBE7-43CE-BE57-2A40-4ABD24953621" },
    { label: "Killjoy", hashcode: "1E58DE9C-4950-5125-93E9-A0AEE9F98746" },
    { label: "Neon", hashcode: "BB2A4828-46EB-8CD1-E765-15848195D751" },
    { label: "Omen", hashcode: "8E253930-4C05-31DD-1B6C-968525494517" },
    { label: "Phoenix", hashcode: "EB93336A-449B-9C1B-0A54-A891F7921D69" },
    { label: "Raze", hashcode: "F94C3B30-42BE-E959-889C-5AA313DBA261" },
    { label: "Reyna", hashcode: "A3BFB853-43B2-7238-A4F1-AD90E9E46BCC" },
    { label: "Sage", hashcode: "569FDD95-4D10-43AB-CA70-79BECC718B46" },
    { label: "Skye", hashcode: "6F2A04CA-43E0-BE17-7F36-B3908627744D" },
    { label: "Sova", hashcode: "DED3520F-4264-BFED-162D-B080E2ABCCF9" },
    { label: "Tejo", hashcode: "B444168C-4E35-8076-DB47-EF9BF368F384" },
    { label: "Vyse", hashcode: "EFBA5359-4016-A1E5-7626-B1AE76895940" },
    { label: "Viper", hashcode: "707EAB51-4836-F488-046A-CDA6BF494859" },
    { label: "Waylay", hashcode: "DF1CB487-4902-002E-5C17-D28E83E78588" },
    { label: "Yoru", hashcode: "7F94D92C-4234-0A36-9646-3A87EB8B5C89" },
].map(agent => ({
    ...agent,
    image: `/images/valorant/agents/${agent.hashcode}.png`,
}));



export const weaponOptions = [
    { label: "Classic", hashcode: "29A0CFAB-485B-F5D5-779A-B59F85E204A8" },
    { label: "Shorty", hashcode: "42DA8CCC-40D5-AFFC-BEEC-15AA47B42EDA" },
    { label: "Frenzy", hashcode: "44D4E95C-4157-0037-81B2-17841BF2E8E3" },
    { label: "Ghost", hashcode: "1BAA85B4-4C70-1284-64BB-6481DFC3BB4E" },
    { label: "Sheriff", hashcode: "E336C6B8-418D-9340-D77F-7A9E4CFE0702" },
    { label: "Stinger", hashcode: "F7E1B454-4AD4-1063-EC0A-159E56B58941" },
    { label: "Spectre", hashcode: "462080D1-4035-2937-7C09-27AA2A5C27A7" },
    { label: "Bucky", hashcode: "910BE174-449B-C412-AB22-D0873436B21B" },
    { label: "Judge", hashcode: "EC845BF4-4F79-DDDA-A3DA-0DB3774B2794" },
    { label: "Bulldog", hashcode: "AE3DE142-4D85-2547-DD26-4E90BED35CF7" },
    { label: "Guardian", hashcode: "4ADE7FAA-4CF1-8376-95EF-39884480959B" },
    { label: "Phantom", hashcode: "EE8E8D15-496B-07AC-E5F6-8FAE5D4C7B1A" },
    { label: "Vandal", hashcode: "9C82E19D-4575-0200-1A81-3EACF00CF872" },
    { label: "Marshall", hashcode: "C4883E50-4494-202C-3EC3-6B8A9284F00B" },
    { label: "Outlaw", hashcode: "5F0AAF7A-4289-3998-D5FF-EB9A5CF7EF5C" },
    { label: "Operator", hashcode: "A03B24D3-4319-996D-0F8C-94BBFBA1DFC7" },
    { label: "Ares", hashcode: "55D8A0F4-4274-CA67-FE2C-06AB45EFDF58" },
    { label: "Odin", hashcode: "63E6C2B6-4A8E-869C-3D4C-E38355226584" },
    { label: "Knife", hashcode: "2F59173C-4BED-B6C3-2191-DEA9B58BE9C7" },
].map(weapon => ({
    ...weapon,
    image: `/images/valorant/weapons/${weapon.hashcode}_killstream.png`,
}));



export const armorOptions = [
    { label: "No Armor", hashcode: "NONE" },
    { label: "Light Armor", hashcode: "4DEC83D5-4902-9AB3-BED6-A7A390761157" },
    { label: "Regen Shield", hashcode: "B1B9086D-41BD-A516-5D29-E3B34A6F1644" },
    { label: "Heavy Armor", hashcode: "822BCAB2-40A2-324E-C137-E09195AD7692" },
].map(armor => ({
    ...armor,
    image: `/images/valorant/armors/${armor.hashcode}.png`,
}));



export const mapOptions = [
    { label: "Abyss", hashcode: "224B0A95-48B9-F703-1BD8-67ACA101A61F" },
    { label: "Ascent", hashcode: "7EAECC1B-4337-BBF6-6AB9-04B8F06B3319" },
    { label: "Bind", hashcode: "2C9D57EC-4431-9C5E-2939-8F9EF6DD5CBA" },
    { label: "Breeze", hashcode: "2FB9A4FD-47B8-4E7D-A969-74B4046EBD53" },
    { label: "Fracture", hashcode: "B529448B-4D60-346E-E89E-00A4C527A405" },
    { label: "Haven", hashcode: "2BEE0DC9-4FFE-519B-1CBD-7FBE763A6047" },
    { label: "Icebox", hashcode: "E2AD5C54-4114-A870-9641-8EA21279579A" },
    { label: "Lotus", hashcode: "2FE4ED3A-450A-948B-6D6B-E89A78E680A9" },
    { label: "Pearl", hashcode: "FD267378-4D1D-484F-FF52-77821ED10DC2" },
    { label: "Split", hashcode: "D960549E-485C-E861-8D71-AA9D1AED12A2" },
    { label: "Sunset", hashcode: "92584FBE-486A-B1B2-9FAA-39B0F486B498" },
].map(map => ({
    ...map,
    image: `/images/valorant/maps/${map.hashcode}_listview.png`,
}));