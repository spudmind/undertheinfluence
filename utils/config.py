# -*- coding: utf-8 -*-

prefixes = [
    u"Sir ",
    u"Mr ",
    u"Ms ",
    u"The Rt Hon "
]

sufixes = [
    u" MP",
    u"Mr ",
    u"Ms ",
    u"The Rt Hon "
]

lords_titles = [
    u"Lady",
    u"Lord",
    u"Earl",
    u"Baroness",
    u"Viscount",
    u"Bishop",
    u"Countess",
    u"Archbishop",
    u"Duke",
    u"Marquess"
]

mapped_positions = [
    (
        u"Parliamentary Under Secretary of State (Minister for Employment Relations",
        u"Parliamentary Under Secretary of State (Minister for Employment Relations, Consumer and Postal Affairs)"
    ),
    (
        u"Parliamentary Secretary for Business, Innovation and Skills Parliamentary Under Secretary of State",
        u"Parliamentary Secretary (Business, Innovation and Skills)"
    )
]

position_entities = [
    u"Parliamentary Under Secretary of State (Minister for Employment Relations"
]


influencer_entities = [
    u"IPSOS Mori",
    u"Ipsos MORI",
    u"Ipsos Mori",
    u"YouGov",
    u"ComRes",
    u"Guardian Media Group"
    u"Social Investment Business Group",
    u"Mansfeider Kupfer Und Messing GMBH",
    u"Pembroke VCT plc",
    u"Woodlands Schools Ltd",
    u"Making It (UK) Ltd",
    u"Phoenix Life Assurance Ltd",
    u"Office of Gordon and Sarah Brown",
    u"The Independent Game Developers",
    u"Transworld Publishers",
    u"Developing Markets Associates Ltd",
    u"Democracy Forum Ltd",
    u"Ambriel Consulting",
    u"Developing Market Associates Ltd",
    u"Royds LLP",
    u"Aegis Tax LLP",
    u"Abu Dhabi",
    u"Government of Mauritius",
    u"United and Cecil Club",
    u"United and Cecil"
    u"Morley and Outwood CLP",
    u"Policy Connect",
    u"RESULTS UK",
    u"Results UK",
    u"The Electrum Group (UK) LLP",
    u"Sightsavers UK",
    u"UK Defence Forum",
    u"JTI UK",
    u"VSO UK",
    u"Conservative Friends of Israel",
    u"Labour Friends of Israel",
    u"Liberal Democrat Friends of Israel",
    u"Connexall",
    u"Lord Sugar of Clapton",
    u"Dellapina Law",
    u"Investec",
    u"Edulink Consultants",
    u"Yeovil Liberal Democrats",
    u"Shura Council of the Kingdom of Saudi Arabia",
    u"The American University in Dubai",
    u"Government of Gibraltar",
    u"Sterling Lord Literistic",
    u"North West Norfolk Patrons Club",
    u"YiMei Capital",
    u"Global Partners Governance",
    u"British University in Egypt",
    u"GovNet Communications",
    u"Catholic Bishops Conference of England and Wales",
    u"Construction Industry Council",
    u"Keltbray Group (Holdings) Ltd",
    u"GR Software and Research Ltd",
    u"LEK Advisory Board",
    u"United & Cecil Club",
    u"Evercore Pan-Asset Capital Management Ltd",
    u"Bar of England and Wales",
    u"Pan Asset Capital Management Ltd",
    u"Taipei Representative Office",
    u"Government of the United Arab Emirates",
    u"Simon and Schuster UK Ltd",
    u"Groupe Eurotunnel",
    u"UCATT",
    u"Government Summit, Dubai",
    u"Huatuo CEO Business Consultant",
    u"Ministry of Foreign Affairs (Saudi Arabia)",
    u"Ministry of Foreign Affairs in Bahrain",
    u"Ministry of Foreign Affairs, Bahrain",
    u"Ministry of Foreign Affairs, Vietnam",
    u"13th Doha Forum",
    u"Ministry of Foreign Affairs, Government of Barbados",
    u"JCB Research",
    u"Press TV",
    u"Garstangs",
    u"R K Harrison",
    u"Perseus books LL",
    u"JCB research",
    u"British-Turkish Tatlidil",
    u"Big Society Capital Bank",
    u"Brenthurst Foundation",
    u"EPIC Private Equity",
    u"NDI",
    u"Electric Infrastructure Security Council",
    u"Hashoo Group",
    u"GovernUp",
    u"Big Society Capital Bank",
    u"Chinese for Labour",
    u"Veolia Environmental Services",
    u"Jamaica Tourist Board",
    u"Government of Taiwan",
    u"Mail on Sunday",
    u"British Transport Police",
    u"British-Spanish Tertulias",
    u"American International University in London",
    u"Medical Aid for Palestinians",
    u"Telegraph Media Group Limited"
    u"Telegraph Media group",
    u"Biteback Publishing Ltd",
    u"Total Politics magazine",
    u"Dods",
    u"Government Knowledge",
    u"International Fund for Animal Welfare",
    u"Friends of the Earth",
    u"Coventry Building Society",
    u"Daily Mail and Mail on Sunday",
    u"Sensortec",
    u"Saliston Ltd",
    u"Gazprom",
    u"Maloja Ltd",
    u"Thermal Engineering Holding Ltd",
    u"AFC Energy",
    u"Mr and Mrs D Wall"
    u"Communication Workers Union",
    u"UNISON",
    u"Ministry of Sound",
    u"Northampton Lib Dem Council Group",
    u"Shell",
    u"Johnson and Johnson",
    u"British Accreditation Council",
    u"British In Vitro Diagnostics Association",
    u"Association of British Pharmaceutical Industries",
    u"National Health Service",
    u"Turner and Townsend",
    u"Business Council for Africa"
    u"Technical and Vocational Education and Training United Kingdom",
    u"English UK",
    u"Advisory Committee on Mathematics Education",
    u"Capital for Enterprise",
    u"Amadeus and Angels Seed Fund",
    u"Ove Arup and Partners",
    u"Sahaviriya Steel Industries UK",
    u"Ford of Britain",
    u"British Phonographic Industries"
    u"British Phonographic Industry",
    u"Infrastructure UK Advisory Panel",
    u"British Cheque and Credit Association"
    u"Advancing UK Aerospace",
    u"Perimeter Institute for Theoretical Physics",
    u"Associated British Foods",
    u"National Association of British and Irish Millers",
    u"Science, Technology, Engineering and Mathematics Network",
    u"Smith School of Enterprise and Environment",
    u"Welsh Joint Education Committee",
    u"Oxford Cambridge and Royal Society of Arts Examinations",
    u"National Skills Academy for Railway Engineering",
    u"Consumer News and Business Channel",
    u"Royal Bank of Scotland",
    u"UK Centre for Economic & Environmental Development",
    u"Royal Society for the Protection of Birds",
    u"The All Party Parliamentary Group on Body Image",
    u"Tata and Sons",
    u"Guangdong Mingyang Wind Power",
    u"Zayed University Dubai & Abu Dhabi",
    u"Abu Dhabi National Oil Company",
    u"Abu Dhabi Council for Economic Development",
    u"Sichuan Yibin Wuliangye Group Co",
    u"Shanghai CP Guojian Pharmaceutical Co"
    u"Business Council for Africa UK",
    u"University of Wolverhampton",
    u"Penzance Harbour and Seafront Working Group",
    u"Solihull Metropolitan Borough Council",
    u"Birmingham and Solihull Local Enterprise Partnership",
    u"London Undergrouns and London Rail",
    u"England and Wales Cricket Board",
    u"Drake and Morgan",
    u"Mark Thompson (BBC)",
    u"Holland and Barrett",
    u"Young Men's Christian Association",
    u"Royal National Institute for the Blind",
    u"England 2018 Bid Team",
    u"Northrop Grumman Remotec UK",
    u"British Union for the Abolition of Vivisection",
    u"Sahara Prime City Limited",
    u"Association of Teachers and Lecturers",
    u"Universities Council for the Education of Teachers",
    u"Union of Shop Distribution and Allied Workers",
    u"Foster and Partners",
    u"Green Templeton College",
    u"Associated British Ports",
    u"West of England Local Enterprise Partnership",
    u"London Borough of Camden",
    u"Newport and District Chamber of Trade and Commerce",
    u"Monmouth and District Chamber of Trade and Commerce",
    u"National Federation for the Blind",
    u"Canadian Minister for Natural Resources",
    u"Sydney and London Properties",
    u"Marshall Aerospace and Defence Group",
    u"Strategic Mailing Partnership for Royal Mail",
    u"City and Guilds in India",
    u"City and Guilds",
    u"Office of the Independent Adjudicator for Higher Education",
    u"British Screen Advisory Council",
    u"Federation of Awarding Bodies and Joint Council for Qualifications",
    u"Scottish and Southern Energy Plc",
    u"Konrad Adenauer Stiftung",
    u"UK Council on Deafness",
    u"Bishop of London",
    u" British Beer and Pub Assc",
    u"The Commission on the Future of Womens Sport",
    u"Power to the Pixel",
    u"Faber and Faber",
    u"Finch and Partners",
    u"The Independent",
    u"Hongkong and Shanghai Ltd",
    u"Burton's Foods Ltd",
    u"National Ignition Facility and Photon Science Directorate",
    u"TRaC Defence and Aerospace Laboratory",
    u"Howard League for Penal Reform",
    u"Stoke on Trent City Council",
    u"German Industry UK",
    u"Rathlin Energy",
    u"Tamboran",
    u"Cuadrilla",
    u"Independent Kidderminster Hospital and Health Concern",
    u"Unite Against Fascism",
    u"Muslim Friends Of Labour",
    u"The Yeovil C.I.F. Trust Fund"
]

mapped_influencers = [
    (u"United & Cecil Club", u"United and Cecil Club"),
    (u"Guardian News & Media Group", u"Guardian News and Media Ltd"),
    (u"Guardian News", u"Guardian News and Media Ltd"),
    (u"Guardian Media Group", u"Guardian News and Media Ltd"),
    (u"Guardian", u"Guardian News and Media Ltd"),
    (u"Telegraph Media Group Limited", u"Telegraph Media Group Ltd"),
    (u"Telegraph Media group", u"Telegraph Media Group Ltd"),
    (u"Telegraph", u"Telegraph Media Group Ltd"),
    (u"Dods", u"Dods Parliamentary Communications Ltd"),
    (u"IPSOS Mori", u"Ipsos Mori"),
    (u"Ipsos MORI", u"Ipsos Mori"),
    (u"Comres", u"ComRes"),
    (u"Pricewaterhouse Coopers", u"PriceWaterhouse Coopers LLP"),
    (u"PricewaterhouseCoopers", u"PriceWaterhouse Coopers LLP"),
    (u"PwC", u"PriceWaterhouse Coopers LLP"),
    (u"JCB Research", u"JCB Research Ltd"),
    (u"J C B Research Ltd", u"JCB Research Ltd"),
    (u"J C B Research", u"JCB Research Ltd"),
    (u"JCB Research Limited", u"JCB Research Ltd"),
    (u"JCB research", u"JCB Research Ltd"),
    (u"UCATT", u"Union of Construction, Allied Trades and Technicians"),
    (u"YouGov", u"YouGov PLC"),
    (u"Ministry of Foreign Affairs in Bahrain", u"Ministry of Foreign Affairs, Bahrain"),
    (u"Ministry of Foreign Affairs (Saudi Arabia)", u"Ministry of Foreign Affairs, Saudi Arabia"),
    (u"Suddhir Chowdhrie", u"Sudhir Choudhrie"),
    (u"Garstangs", u"Garstangs Burrows Bussin"),
    (u"Populus", u"Populus Ltd"),
    (u"Populus Limited", u"Populus Ltd"),
    (u"Perseus books LL", u"Perseus Books, LLC"),
    (u"BASF", u"BASF PLC"),
    (u"Shura Council of Kingdom Saudi Arabia", u"Shura Council of the Kingdom of Saudi Arabia"),
    (u"ResultsUK", u"Results UK"),
    (u"RESULTS UK", u"Results UK"),
    (u"Shell", u"Royal Dutch Shell Group"),
    (u"BAE", u"BAE Systems"),
    (u"Johnson and Johnson", u"Johnson & Johnson"),
    (u"National Health Service", u"NHS"),
    (u"BT plc", u"BT"),
    (u"British Telecom plc", u"BT"),
    (u"Everything Everywhere", u"EE"),
    (u"EverythingEverywhere", u"EE"),
    (u"London Undergrouns and London Rail", u"London Underground and London Rail"),
    (u"Young Men's Christian Association", u"YMCA"),
    (u"British Phonographic Industries", u"British Phonographic Industry"),
    (u"Locog", u"LOCOG"),
    (u"Channel Four", u"Channel 4"),
    (u"EADS", u"European Aeronautic Space & Defence Company"),
    (u"Faber and Faber", u"Faber & Faber"),
    (u"The Independent Game Developers", u"The Independent Game Developers' Association"),
    (u"SOAS", u"School of Oriental and African Studies"),
    (u"AA", u"The AA"),
    (u"TFL", u"Transport for London"),
    (u"Guild HE", u"GuildHE"),
    (u"Babcock", u"Babcock International Group"),
    (u"Beggars", u"Beggars Group"),
    (u"Talktalk", u"Talk Talk"),
    (u"TalkTalk", u"Talk Talk"),
    (u"SERCO", u"Serco"),
    (u"Bbc", u"BBC"),
    (u"Ministry of Sound Group Ltd", u"Ministry of Sound"),
    (u"Ibm", u"IBM"),
    #(u"Unite", u"Unite the Union"),
]


party_entities = [
    u"Labour Party",
    u"Labour",
    u"Alliance Party of Northern Ireland",
    u"Alliance Party",
    u"Alliance",
    u"Democratic Unionist Party",
    u"DUP",
    u"Sinn Fein",
    u"Conservative Party",
    u"Conservative",
    u"Liberal Democrat Party",
    u"Liberal Democrats",
    u"Liberal Democrat",
    u"Plaid Cymru",
    u"Independent",
    u"Social Democratic and Labour Party",
    u"Scottish National Party",
    u"Greens",
    u"Green Party",
    u"Speaker",
    u"UK Independence Party",
    u"UKIP",
    u"Co-operative Party",
    u"We Demand A Referendum Now",
    u"BNP",
    u"Respect",
    u"British National Party",
    u"NO2EU",
    u"English Democrats",
    u"Crossbench",
    u"Bishop",
    u"Scottish Socialist Party",
    u"The Progressive Democratic Party",
    u"The Liberal Party",
    u"Scottish Green Party",
    u"The People's Alliance",
    u"Legalise Cannabis Alliance",
    u"Christian Peoples Alliance",
    u"The New Party",
    u"ProLife",
    u"The Blah Party"
]

mapped_lobbyists = [
    (u"A4e", u"A4E"),
    (u"Aardvark Reputation Management Ltd", u"Aardvark Communications"),
    (u"Apco", u"Apco Worldwide"),
    (u"Bellenden", u"Bellenden Limited"),
    (u"Belgrave", u"Belgrave Communications"),
    (u"Calacus", u"Calacus Public Relations"),
    (u"Champollion", u"Champollion Communications Ltd"),
    (u"Champollion Communications Consultancy", u"Champollion Communications Ltd"),
    (u"Curtin Communications Limited", u"Curtin Communications Ltd"),
    (u"Communications Group, The", u"The Communications Group"),
    (u"Derbyshire Council", u"Derbyshire County Council"),
    (u"Edelman", u"Edelman Public Affairs"),
    (u"Grayling", u"Grayling Public Affairs"),
    (u"Graylng", u"Grayling Public Affairs"),
    (u"Good Relations Brand Communications", u"Good Relations"),
    (u"Good Relations Political Communications", u"Good Relations"),
    (u"HKStrategies", u"H+K Strategies"),
    (u"Hanover", u"Hanover Communications International Ltd"),
    (u"Hanover Communications", u"Hanover Communications International Ltd"),
    (u"ICG (Insight Consulting Group)", u"Insight Consulting Group"),
    (u"Instinctif Partners, Public Policy Practice", u"Insight Consulting Group"),
    (u"Jbp", u"Jbp Pr"),
    (u"Kinetic Communications", u"Kinetic Communications Ltd"),
    (u"Lansons Public Affairs", u"Lansons"),
    (u"Lansons Public Affairs and Regulatory Consulting", u"Lansons"),
    (u"London Chamber of Commerce", u"London Chamber of Commerce and Industry"),
    (u"London Chamber of Commerce & Industry", u"London Chamber of Commerce and Industry"),
    (u"London Communication Agency", u"London Communications Agency"),
    (u"M&N Place", u"M&N Place Limited"),
    (u"M&N Communications", u"M&N Place Limited"),
    (u"M&N Communications Limited", u"M&N Place Limited"),
    (u"Marks & Spencers", u"Marks & Spencer"),
    (u"Marks & Spensers", u"Marks & Spencer"),
    (u"Munro & Forster", u"Munro & Forster"),
    (u"Munro & Forster (Political and Stakeholder Counsel Team)", u"Munro & Forster"),
    (u"Munro & Foster", u"Munro & Forster"),
    (u"Nationwide", u"Nationwide Building Society"),
    (u"Newgate Communications", u"Newgate Communications LLP"),
    (u"PB Political Consultation", u"PB Political Consulting"),
    (u"Political Developments Limited", u"Political Developments Ltd"),
    (u"Portland", u"Portland Communications"),
    (u"Portland PR", u"Portland Communications"),
    (u"Public Relations Consultancy Association", u"Public Relations Consultants Association"),
    (u"Remarkable", u"Remarkable Group"),
    (u"The Communication Group plc", u"The Communication Group"),
    (u"The Communication Group plc.", u"The Communication Group"),
    (u"The Communications Group", u"The Communication Group"),
    (u"The Whitehouse Consultancy", u"The Whitehouse Consultancy Ltd"),
    (u"Ebay UK Ltd", u"eBay UK Ltd"),
    (u"Weber Shandwick", u"Weber Shandwick Public Affairs"),
]

mapped_mps = [
    (u"Nicholas Boles", u"Nick Boles"),
    (u"Nicholas Clegg", u"Nick Clegg"),
    (u"Vincent Cable", u"Vince Cable"),
    (u"Brian H Donohoe", u"Brian Donohoe"),
    (u"Susan Elan Jones", u"Susan Jones"),
    (u"Jeffrey M Donaldson", u"Jeffrey Donaldson"),
    (u"Edward Miliband", u"Ed Miliband"),
    (u"Edward Milliband", u"Ed Miliband"),
    (u"Edward Balls", u"Ed Balls"),
    (u"Michael Denzil Xavier Portillo", u"Michael Portillo"),
    (u"Christopher Huhne", u"Chris Huhne"),
]

mp_entities = [
    u"Michael Denzil Xavier Portillo"
]


mapped_parties = [
    (u"DUP", u"Democratic Unionist Party"),
    (u"UKIP", u"UK Independence Party"),
    (u"Greens", u"Green Party"),
    (u"Respect", u"Respect Party"),
    (u"BNP", u"British National Party"),
    (u"Alliance Party", u"Alliance Party of Northern Ireland"),
    (u"Alliance", u"Alliance Party of Northern Ireland"),
    (u"Liberal Democrat Party", u"Liberal Democrats"),
    (u"Liberal Democrat", u"Liberal Democrats"),
    (u"Conservative", u"Conservative Party"),
    (u"Labour", u"Labour Party"),
    (u"Bishop", u"The Church of England")
]

mapped_party_images = {
    u"Democratic Unionist Party": "http://www.conservativehome.com/wp-content/uploads/2015/01/DUP-logo.png",
    u"UK Independence Party": "http://upload.wikimedia.org/wikipedia/en/d/d2/UKIP_logo.png",
    u"British National Party": "http://upload.wikimedia.org/wikipedia/en/9/96/British_National_Party.svg",
    u"Alliance Party of Northern Ireland": "http://upload.wikimedia.org/wikipedia/commons/b/be/Alliance_Party_of_Northern_Ireland_logo.svg",
    u"Liberal Democrats": "http://d3n8a8pro7vhmx.cloudfront.net/libdems/pages/345/meta_images/original/BirdOfLiberty-01_600px315px.png?1400231624",
    u"Conservative Party": "http://upload.wikimedia.org/wikipedia/en/thumb/b/b6/Conservative_logo_2006.svg/1280px-Conservative_logo_2006.svg.png",
    u"Labour Party": "http://myhessle.com/wp-content/uploads/2012/10/labour-rose.png",
    u"The Church of England": "http://www.mountsorrel.leicester.anglican.org/images/Church_Of_England_Logo_col_0.20.gif",
    u"Scottish National Party": "http://cdbu.org.uk/wp-content/uploads/2015/01/SNP-logo-with-name.jpg",
    u"Independent": None,
    u"Sinn Fein": "http://sluggerotoole.com/wp-content/uploads/2011/02/sinn-fein-logo.jpeg",
    u"Crossbench": None,
    u"Plaid Cymru": "http://www.partyof.wales/uploads/Logos/plaid_poppy.jpg",
    u"Speaker": None,
    u"Green Party": "https://greenparty.org.uk/assets/logos/GPLogoWorldGreenForWeb.jpg",
    u"Respect Party": "http://www.justcurious.co.za/wp-content/uploads/2012/05/respect.jpg.gif",
    u"None": None
}


mapped_lords = [
    (u"Baroness Adams", u"Baroness Adams of Craigielea"),
    (u"Baroness Anelay", u"Baroness Anelay of St Johns"),
    (u"Baroness Armstrong", u"Baroness Armstrong of Hill Top"),
    (u"Baroness Ashton", u"Baroness Ashton of Upholland"),
    (u"Baroness Bakewell", u"Baroness Bakewell of Hardington Mandeville"),
    (u"Baroness Bonham-Carter", u"Baroness Bonham-Carter of Yarnbury"),
    (u"Baroness Bottomley", u"Baroness Bottomley of Nettlestone"),
    (u"Baroness Susan Catherine Campbell", u"Baroness Campbell of Loughborough"),
    (u"Baroness Jane Campbell", u"Baroness Campbell of Surbiton"),
    (u"Baroness Chalker", u"Baroness Chalker of Wallasey"),
    (u"Baroness Chisholm", u"Baroness Chisholm of Owlpen"),
    (u"Baroness Clark", u"Baroness Clark of Calton"),
    (u"Baroness Cohen", u"Baroness Cohen of Pimlico"),
    (u"Baroness Dean", u"Baroness Dean of Thornton-le-Fylde"),
    (u"Baroness Eccles", u"Baroness Eccles of Moulton"),
    (u"Baroness Evans", u"Baroness Evans of Bowes Park"),
    (u"Baroness Falkner", u"Baroness Falkner of Margravine"),
    (u"Baroness Farrington", u"Baroness Farrington of Ribbleton"),
    (u"Baroness Finlay", u"Baroness Finlay of Llandaff"),
    (u"Baroness Garden", u"Baroness Garden of Frognal"),
    (u"Baroness Gardner", u"Baroness Gardner of Parkes"),
    (u"Baroness Gibson", u"Baroness Gibson of Market Rasen"),
    (u"Baroness Gould", u"Baroness Gould of Potternewton"),
    (u"Baroness Hale", u"Baroness Hale of Richmond"),
    (u"Baroness Harding", u"Baroness Harding of Winscombe"),
    (u"Baroness Harris", u"Baroness Harris of Richmond"),
    (u"Baroness Hayter", u"Baroness Hayter of Kentish Town"),
    (u"Baroness Healy", u"Baroness Healy of Primrose Hill"),
    (u"Baroness Hilton", u"Baroness Hilton of Eggardon"),
    (u"Baroness Hodgson", u"Baroness Hodgson of Abinger"),
    (u"Baroness Hollis", u"Baroness Hollis of Heigham"),
    (u"Baroness Howarth", u"Baroness Howarth of Breckland"),
    (u"Baroness Howe", u"Baroness Howe of Idlicote"),
    (u"Baroness Howells", u"Baroness Howells of St Davids"),
    (u"Baroness Hughes", u"Baroness Hughes of Stretford"),
    (u"Baroness James", u"Baroness James of Holland Park"),
    (u"Baroness Jay", u"Baroness Jay of Paddington"),
    (u"Baroness Jenkin", u"Baroness Jenkin of Kennington"),
    (u"Baroness Jennifer Helen Jones", u"Baroness Jones of Moulsecoomb"),
    (u"Baroness Margaret Jones", u"Baroness Jones of Whitchurch"),
    (u"Baroness Alicia Pamela Kennedy", u"Baroness Kennedy of Cradley"),
    (u"Baroness Helena Kennedy", u"Baroness Kennedy of The Shaws"),
    (u"Baroness King", u"Baroness King of Bow"),
    (u"Baroness Kinnock", u"Baroness Kinnock of Holyhead"),
    (u"Baroness Knight", u"Baroness Knight of Collingtree"),
    (u"Baroness Lane-Fox", u"Baroness Lane-Fox of Soho"),
    (u"Baroness Lawrence", u"Baroness Lawrence of Clarendon"),
    (u"Baroness Liddell", u"Baroness Liddell of Coatdyke"),
    (u"Baroness Linklater", u"Baroness Linklater of Butterstone"),
    (u"Baroness Lister", u"Baroness Lister of Burtersett"),
    (u"Baroness Masham", u"Baroness Masham of Ilton"),
    (u"Baroness Doreen Massey", u"Baroness Massey of Darwen"),
    (u"Baroness Genista McIntosh", u"Baroness McIntosh of Hudnall"),
    (u"Baroness Susan Miller", u"Baroness Miller of Chilthorne Domer"),
    (u"Baroness Doreen Miller", u"Baroness Miller of Hendon"),
    (u"Baroness Delyth Morgan", u"Baroness Morgan of Drefelin"),
    (u"Baroness Mair Eluned Morgan", u"Baroness Morgan of Ely"),
    (u"Baroness Sally Morgan", u"Baroness Morgan of Huyton"),
    (u"Baroness Patricia Morris", u"Baroness Morris of Bolton"),
    (u"Baroness Estelle Morris", u"Baroness Morris of Yardley"),
    (u"Baroness Nicholson", u"Baroness Nicholson of Winterbourne"),
    (u"Baroness O'Neill", u"Baroness O'Neill of Bengarve"),
    (u"Baroness Paisley", u"Baroness Paisley of St George's"),
    (u"Baroness Perry", u"Baroness Perry of Southwark"),
    (u"Baroness Platt", u"Baroness Platt of Writtle"),
    (u"Baroness Ramsay", u"Baroness Ramsay of Cartvale"),
    (u"Baroness Rendell", u"Baroness Rendell of Babergh"),
    (u"Baroness Richardson", u"Baroness Richardson of Calow"),
    (u"Baroness Royall", u"Baroness Royall of Blaisdon"),
    (u"Baroness Scotland", u"Baroness Scotland of Asthal"),
    (u"Baroness Scott", u"Baroness Scott of Needham Market"),
    (u"Baroness Shackleton", u"Baroness Shackleton of Belgravia"),
    (u"Baroness Sharp", u"Baroness Sharp of Guildford"),
    (u"Baroness Shephard", u"Baroness Shephard of Northwold"),
    (u"Baroness Angela Evans Smith", u"Baroness Smith of Basildon"),
    (u"Baroness Elizabeth Smith", u"Baroness Smith of Gilmorehill"),
    (u"Baroness Julie Elizabeth Smith", u"Baroness Smith of Newnham"),
    (u"Baroness Stowell", u"Baroness Stowell of Beeston"),
    (u"Baroness Symons", u"Baroness Symons of Vernham Dean"),
    (u"Baroness Ann Taylor", u"Baroness Taylor of Bolton"),
    (u"Baroness Susan Thomas", u"Baroness Thomas of Walliswood"),
    (u"Baroness Celia Thomas", u"Baroness Thomas of Winchester"),
    (u"Baroness Turner", u"Baroness Turner of Camden"),
    (u"Baroness Tyler", u"Baroness Tyler of Enfield"),
    (u"Baroness Wall", u"Baroness Wall of New Barnet"),
    (u"Baroness Warwick", u"Baroness Warwick of Undercliffe"),
    (u"Baroness Shirley Williams", u"Baroness Williams of Crosby"),
    (u"Baroness Susan Frances Maria Williams", u"Baroness Williams of Trafford"),
    (u"Baroness Wolf", u"Baroness Wolf of Dulwich"),
    (u"Baroness Lola Young", u"Baroness Young of Hornsey"),
    (u"Baroness Barbara Young", u"Baroness Young of Old Scone"),
    (u"Lady Saltoun", u"Lady Saltoun of Abernethy"),
    (u"Lord Ahmad", u"Lord Ahmad of Wimbledon"),
    (u"Lord Allan", u"Lord Allan of Hallam"),
    (u"Lord Allen", u"Lord Allen of Kensington"),
    (u"Lord Alton", u"Lord Alton of Liverpool"),
    (u"Lord Anderson", u"Lord Anderson of Swansea"),
    (u"Lord Archer", u"Lord Archer of Weston-super-Mare"),
    (u"Lord Armstrong", u"Lord Armstrong of Ilminster"),
    (u"Lord Ashdown", u"Lord Ashdown of Norton-sub-Hamdon"),
    (u"Lord Ashton", u"Lord Ashton of Hyde"),
    (u"Lord Astor", u"Lord Astor of Hever"),
    (u"Lord Baker", u"Lord Baker of Dorking"),
    (u"Lord Barber", u"Lord Barber of Tewkesbury"),
    (u"Lord Bassam", u"Lord Bassam of Brighton"),
    (u"Lord Fitzhardinge Berkeley", u"Lord Berkeley of Knighton"),
    (u"Lord Guy Vaughan Black", u"Lord Black of Brentwood"),
    (u"Lord Conrad Black", u"Lord Black of Crossharbour"),
    (u"Lord Blair", u"Lord Blair of Boughton"),
    (u"Lord Blyth", u"Lord Blyth of Rowington"),
    (u"Lord Boswell", u"Lord Boswell of Aynho"),
    (u"Lord Bourne", u"Lord Bourne of Aberystwyth"),
    (u"Lord Boyd", u"Lord Boyd of Duncansby"),
    (u"Lord Brabazon", u"Lord Brabazon of Tara"),
    (u"Lord Brittan", u"Lord Brittan of Spennithorne"),
    (u"Lord Clive Brooke", u"Lord Brooke of Alverthorpe"),
    (u"Lord Peter Brooke", u"Lord Brooke of Sutton Mandeville"),
    (u"Lord Brooks", u"Lord Brooks of Tremorfa"),
    (u"Lord Brown", u"Lord Brown of Eaton-under-Heywood"),
    (u"Lord Wallace Browne", u"Lord Browne of Belmont"),
    (u"Lord Desmond Henry Browne", u"Lord Browne of Ladyton"),
    (u"Lord John Browne", u"Lord Browne of Madingley"),
    (u"Lord Butler", u"Lord Butler of Brockwell"),
    (u"Lord Ewen Cameron", u"Lord Cameron of Dillington"),
    (u"Lord Kenneth Cameron", u"Lord Cameron of Lochbroom"),
    (u"Lord Carey", u"Lord Carey of Clifton"),
    (u"Lord Carlile", u"Lord Carlile of Berriew"),
    (u"Lord Carrington", u"Lord Carrington of Fulham"),
    (u"Lord Stephen Andrew Carter", u"Lord Carter of Barnes"),
    (u"Lord Patrick Carter", u"Lord Carter of Coles"),
    (u"Lord Cavendish", u"Lord Cavendish of Furness"),
    (u"Lord Clark", u"Lord Clark of Windermere"),
    (u"Lord Tony Clarke", u"Lord Clarke of Hampstead"),
    (u"Lord Anthony Peter Clarke", u"Lord Clarke of Stone-cum-Ebony"),
    (u"Lord Raymond Edward Harry Collins", u"Lord Collins of Highbury"),
    (u"Lord Lawrence Antony Collins", u"Lord Collins of Mapesbury"),
    (u"Lord Cooper", u"Lord Cooper of Windrush"),
    (u"Lord Cope", u"Lord Cope of Berkeley"),
    (u"Lord Craig", u"Lord Craig of Radley"),
    (u"Lord Cullen", u"Lord Cullen of Whitekirk"),
    (u"Lord Cunningham", u"Lord Cunningham of Felling"),
    (u"Lord Currie", u"Lord Currie of Marylebone"),
    (u"Lord Curry", u"Lord Curry of Kirkharle"),
    (u"Lord Darzi", u"Lord Darzi of Denham"),
    (u"Lord Davidson", u"Lord Davidson of Glen Clova"),
    (u"Lord Evan Mervyn Davies", u"Lord Davies of Abersoch"),
    (u"Lord Garfield Davies", u"Lord Davies of Coity"),
    (u"Lord Bryan Davies", u"Lord Davies of Oldham"),
    (u"Lord John Quentin Davies", u"Lord Davies of Stamford"),
    (u"Lord Eden", u"Lord Eden of Winton"),
    (u"Lord John Evans", u"Lord Evans of Parkside"),
    (u"Lord Matthew Evans", u"Lord Evans of Temple Guiting"),
    (u"Lord David Evans", u"Lord Evans of Watford"),
    (u"Lord Jonathan Douglas Evans", u"Lord Evans of Weardale"),
    (u"Lord Falconer", u"Lord Falconer of Thoroton"),
    (u"Lord Faulkner", u"Lord Faulkner of Worcester"),
    (u"Lord Feldman", u"Lord Feldman of Elstree"),
    (u"Lord Fellowes", u"Lord Fellowes of West Stafford"),
    (u"Lord Forsyth", u"Lord Forsyth of Drumlean"),
    (u"Lord Foster", u"Lord Foster of Bishop Auckland"),
    (u"Lord Foulkes", u"Lord Foulkes of Cumnock"),
    (u"Lord Gardiner", u"Lord Gardiner of Kimble"),
    (u"Lord Goddard", u"Lord Goddard of Stockport"),
    (u"Lord Goff", u"Lord Goff of Chieveley"),
    (u"Lord Gordon", u"Lord Gordon of Strathblane"),
    (u"Lord Grade", u"Lord Grade of Yarmouth"),
    (u"Lord Graham", u"Lord Graham of Edmonton"),
    (u"Lord Andrew Fleming Green", u"Lord Green of Deddington"),
    (u"Lord Stephen Keith Green", u"Lord Green of Hurstpierpoint"),
    (u"Lord Lesley Griffiths", u"Lord Griffiths of Burry Port"),
    (u"Lord Brian Griffiths", u"Lord Griffiths of Fforestfach"),
    (u"Lord Guthrie", u"Lord Guthrie of Craigiebank"),
    (u"Lord Hall", u"Lord Hall of Birkenhead"),
    (u"Lord Hamilton", u"Lord Hamilton of Epsom"),
    (u"Lord Hannay", u"Lord Hannay of Chiswick"),
    (u"Lord Harries", u"Lord Harries of Pentregarth"),
    (u"Lord Toby Harris", u"Lord Harris of Haringey"),
    (u"Lord Philip Harris", u"Lord Harris of Peckham"),
    (u"Lord Hart", u"Lord Hart of Chilton"),
    (u"Lord Hastings", u"Lord Hastings of Scarisbrick"),
    (u"Lord Hennessy", u"Lord Hennessy of Nympsfield"),
    (u"Lord Hill", u"Lord Hill of Oareford"),
    (u"Lord Hodgson", u"Lord Hodgson of Astley Abbotts"),
    (u"Lord Holmes", u"Lord Holmes of Richmond"),
    (u"Lord James Hope", u"Lord Hope of Craighead"),
    (u"Lord David Hope", u"Lord Hope of Thornes"),
    (u"Lord Michael Howard", u"Lord Howard of Lympne"),
    (u"Lord Greville Howard", u"Lord Howard of Rising"),
    (u"Lord Howarth", u"Lord Howarth of Newport"),
    (u"Lord Howe", u"Lord Howe of Aberavon"),
    (u"Lord Howell", u"Lord Howell of Guildford"),
    (u"Lord Howie", u"Lord Howie of Troon"),
    (u"Lord Robert Hughes", u"Lord Hughes of Woodside"),
    (u"Lord Julian Hunt", u"Lord Hunt of Chesterton"),
    (u"Lord Philip Hunt", u"Lord Hunt of Kings Heath"),
    (u"Lord David Hunt", u"Lord Hunt of Wirral"),
    (u"Lord Hurd", u"Lord Hurd of Westwell"),
    (u"Lord Hutton", u"Lord Hutton of Furness"),
    (u"Lord Irvine", u"Lord Irvine of Lairg"),
    (u"Lord James", u"Lord James of Blackheath"),
    (u"Lord Janner", u"Lord Janner of Braunstone"),
    (u"Lord Jay", u"Lord Jay of Ewelme"),
    (u"Lord Jenkin", u"Lord Jenkin of Roding"),
    (u"Lord Digby Jones", u"Lord Jones of Birmingham"),
    (u"Lord Nigel Jones", u"Lord Jones of Cheltenham"),
    (u"Lord Kennedy", u"Lord Kennedy of Southwark"),
    (u"Lord John Kerr", u"Lord Kerr of Kinlochard"),
    (u"Lord Brian Francis Kerr", u"Lord Kerr of Tonaghmore"),
    (u"Lord Kilpatrick", u"Lord Kilpatrick of Kincraig"),
    (u"Lord Tom King", u"Lord King of Bridgwater"),
    (u"Lord Mervyn Allister King", u"Lord King of Lothbury"),
    (u"Lord Kirkwood", u"Lord Kirkwood of Kirkhope"),
    (u"Lord Knight", u"Lord Knight of Weymouth"),
    (u"Lord Lamont", u"Lord Lamont of Lerwick"),
    (u"Lord Lang", u"Lord Lang of Monkton"),
    (u"Lord Lawson", u"Lord Lawson of Blaby"),
    (u"Lord Lea", u"Lord Lea of Crondall"),
    (u"Lord Leach", u"Lord Leach of Fairford"),
    (u"Lord Lee", u"Lord Lee of Trafford"),
    (u"Lord Leigh", u"Lord Leigh of Hurley"),
    (u"Lord Lester", u"Lord Lester of Herne Hill"),
    (u"Lord Levene", u"Lord Levene of Portsoken"),
    (u"Lord Lewis", u"Lord Lewis of Newnham"),
    (u"Lord Livingston", u"Lord Livingston of Parkhead"),
    (u"Lord Lloyd", u"Lord Lloyd of Berwick"),
    (u"Lord Low", u"Lord Low of Dalston"),
    (u"Lord MacGregor", u"Lord MacGregor of Pulham Market"),
    (u"Lord MacKenzie", u"Lord MacKenzie of Culkein"),
    (u"Lord MacLaurin", u"Lord MacLaurin of Knebworth"),
    (u"Lord Macaulay", u"Lord Macaulay of Bragar"),
    (u"Lord Kenneth Donald John Macdonald", u"Lord Macdonald of River Glaven"),
    (u"Lord Gus Macdonald", u"Lord Macdonald of Tradeston"),
    (u"Lord Macfarlane", u"Lord Macfarlane of Bearsden"),
    (u"Lord James Mackay", u"Lord Mackay of Clashfern"),
    (u"Lord Donald Mackay", u"Lord Mackay of Drumadoon"),
    (u"Lord Mackenzie", u"Lord Mackenzie of Framwellgate"),
    (u"Lord Mackie", u"Lord Mackie of Benshie"),
    (u"Lord Maclennan", u"Lord Maclennan of Rogart"),
    (u"Lord Magan", u"Lord Magan of Castletown"),
    (u"Lord Maginnis", u"Lord Maginnis of Drumglass"),
    (u"Lord Marks", u"Lord Marks of Henley-on-Thames"),
    (u"Lord Martin", u"Lord Martin of Springburn"),
    (u"Lord Mason", u"Lord Mason of Barnsley"),
    (u"Lord May", u"Lord May of Oxford"),
    (u"Lord Mayhew", u"Lord Mayhew of Twysden"),
    (u"Lord McColl", u"Lord McColl of Dulwich"),
    (u"Lord McConnell", u"Lord McConnell of Glenscorrodale"),
    (u"Lord McFall", u"Lord McFall of Alcluith"),
    (u"Lord McKenzie", u"Lord McKenzie of Luton"),
    (u"Lord Molyneaux", u"Lord Molyneaux of Killead"),
    (u"Lord Montagu", u"Lord Montagu of Beaulieu"),
    (u"Lord Moore", u"Lord Moore of Lower Marsh"),
    (u"Lord John Morris", u"Lord Morris of Aberavon"),
    (u"Lord William Morris", u"Lord Morris of Handsworth"),
    (u"Lord Neill", u"Lord Neill of Bladen"),
    (u"Lord Neuberger", u"Lord Neuberger of Abbotsbury"),
    (u"Lord Nicholls", u"Lord Nicholls of Birkenhead"),
    (u"Lord Norton", u"Lord Norton of Louth"),
    (u"Lord O'Neill", u"Lord O'Neill of Clackmannan"),
    (u"Lord Oakeshott", u"Lord Oakeshott of Seagrove Bay"),
    (u"Lord Palmer", u"Lord Palmer of Childs Hill"),
    (u"Lord Palumbo", u"Lord Palumbo of Southwark"),
    (u"Lord Adam Patel", u"Lord Patel of Blackburn"),
    (u"Lord Kamlesh Patel", u"Lord Patel of Bradford"),
    (u"Lord Patten", u"Lord Patten of Barnes"),
    (u"Lord Pearson", u"Lord Pearson of Rannoch"),
    (u"Lord Andrew Phillips", u"Lord Phillips of Sudbury"),
    (u"Lord Nicholas Phillips", u"Lord Phillips of Worth Matravers"),
    (u"Lord Plant", u"Lord Plant of Highfield"),
    (u"Lord Ponsonby", u"Lord Ponsonby of Shulbrede"),
    (u"Lord Powell", u"Lord Powell of Bayswater"),
    (u"Lord Purvis", u"Lord Purvis of Tweed"),
    (u"Lord Rees", u"Lord Rees of Ludlow"),
    (u"Lord Reid", u"Lord Reid of Cardowan"),
    (u"Lord Renfrew", u"Lord Renfrew of Kaimsthorn"),
    (u"Lord Renton", u"Lord Renton of Mount Harry"),
    (u"Lord Renwick", u"Lord Renwick of Clifton"),
    (u"Lord Richards", u"Lord Richards of Herstmonceux"),
    (u"Lord Wyn Roberts", u"Lord Roberts of Conwy"),
    (u"Lord Roger Roberts", u"Lord Roberts of Llandudno"),
    (u"Lord Robertson", u"Lord Robertson of Port Ellen"),
    (u"Lord Bill Rodgers", u"Lord Rodgers of Quarry Bank"),
    (u"Lord Richard Rogers", u"Lord Rogers of Riverside"),
    (u"Lord Rose", u"Lord Rose of Monewden"),
    (u"Lord Ryder", u"Lord Ryder of Wensum"),
    (u"Lord John Sainsbury", u"Lord Sainsbury of Preston Candover"),
    (u"Lord David Sainsbury", u"Lord Sainsbury of Turville"),
    (u"Lord Sanderson", u"Lord Sanderson of Bowden"),
    (u"Lord Saville", u"Lord Saville of Newdigate"),
    (u"Lord Scott", u"Lord Scott of Foscote"),
    (u"Lord Selkirk", u"Lord Selkirk of Douglas"),
    (u"Lord Shaw", u"Lord Shaw of Northstead"),
    (u"Lord Sheppard", u"Lord Sheppard of Didgemere"),
    (u"Lord Sherbourne", u"Lord Sherbourne of Didsbury"),
    (u"Lord Shutt", u"Lord Shutt of Greetland"),
    (u"Lord Simon", u"Lord Simon of Highbury"),
    (u"Lord Simpson", u"Lord Simpson of Dunkeld"),
    (u"Lord Singh", u"Lord Singh of Wimbledon"),
    (u"Lord Trevor Smith", u"Lord Smith of Clifton"),
    (u"Lord Chris Smith", u"Lord Smith of Finsbury"),
    (u"Lord Robert Haldane Smith", u"Lord Smith of Kelvin"),
    (u"Lord Peter Smith", u"Lord Smith of Leigh"),
    (u"Lord Soulsby", u"Lord Soulsby of Swaffham Prior"),
    (u"Lord St John", u"Lord St John of Bletso"),
    (u"Lord Steel", u"Lord Steel of Aikwood"),
    (u"Lord Sterling", u"Lord Sterling of Plaistow"),
    (u"Lord Stern", u"Lord Stern of Brentford"),
    (u"Lord John Stevens", u"Lord Stevens of Kirkwhelpington"),
    (u"Lord David Stevens", u"Lord Stevens of Ludgate"),
    (u"Lord Robert Wilfrid Stevenson", u"Lord Stevenson of Balmacara"),
    (u"Lord Henry Stevenson", u"Lord Stevenson of Coddenham"),
    (u"Lord Stoddart", u"Lord Stoddart of Swindon"),
    (u"Lord Stone", u"Lord Stone of Blackheath"),
    (u"Lord Stoneham", u"Lord Stoneham of Droxford"),
    (u"Lord Sutherland", u"Lord Sutherland of Houndwood"),
    (u"Lord Tom Taylor", u"Lord Taylor of Blackburn"),
    (u"Lord Matthew Owen John Taylor", u"Lord Taylor of Goss Moor"),
    (u"Lord John Derek Taylor", u"Lord Taylor of Holbeach"),
    (u"Lord John Taylor", u"Lord Taylor of Warwick"),
    (u"Lord Sir Roger John Laugharne Thomas", u"Lord Thomas of Cwmgiedd"),
    (u"Lord Martin Thomas", u"Lord Thomas of Gresford"),
    (u"Lord Terence Thomas", u"Lord Thomas of Macclesfield"),
    (u"Lord Hugh Thomas", u"Lord Thomas of Swynnerton"),
    (u"Lord Turner", u"Lord Turner of Ecchinswell"),
    (u"Lord Vallance", u"Lord Vallance of Tummel"),
    (u"Lord Vincent", u"Lord Vincent of Coleshill"),
    (u"Lord Wade", u"Lord Wade of Chorlton"),
    (u"Lord Waldegrave", u"Lord Waldegrave of North Hill"),
    (u"Lord Michael Walker", u"Lord Walker of Aldringham"),
    (u"Lord Robert Walker", u"Lord Walker of Gestingthorpe"),
    (u"Lord William Wallace", u"Lord Wallace of Saltaire"),
    (u"Lord James Robert Wallace", u"Lord Wallace of Tankerness"),
    (u"Lord Walton", u"Lord Walton of Detchant"),
    (u"Lord Mike Watson", u"Lord Watson of Invergowrie"),
    (u"Lord Alan Watson", u"Lord Watson of Richmond"),
    (u"Lord West", u"Lord West of Spithead"),
    (u"Lord Michael Charles Williams", u"Lord Williams of Baglan"),
    (u"Lord Charles Williams", u"Lord Williams of Elvel"),
    (u"Lord Rowan Douglas Williams", u"Lord Williams of Oystermouth"),
    (u"Lord Williamson", u"Lord Williamson of Horton"),
    (u"Lord Willis", u"Lord Willis of Knaresborough"),
    (u"Lord Richard Wilson", u"Lord Wilson of Dinton"),
    (u"Lord David Wilson", u"Lord Wilson of Tillyorn"),
    (u"Lord Simon Adam Wolfson", u"Lord Wolfson of Aspley Guise"),
    (u"Lord David Wolfson", u"Lord Wolfson of Sunningdale"),
    (u"Lord Wood", u"Lord Wood of Anfield"),
    (u"Lord Woolmer", u"Lord Woolmer of Leeds"),
    (u"Lord Wright", u"Lord Wright of Richmond"),
    (u"Lord David Young", u"Lord Young of Graffham"),
    (u"Lord Tony Young", u"Lord Young of Norwood Green"),
    (u"Viscount Allenby", u"Viscount Allenby of Megiddo"),
    (u"Viscount Colville", u"Viscount Colville of Culross"),
    (u"Viscount Montgomery", u"Viscount Montgomery of Alamein"),
    (u"Viscount Younger", u"Viscount Younger of Leckie")
]