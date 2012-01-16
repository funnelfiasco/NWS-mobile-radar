#!/usr/bin/perl

###################
#
# nws_mobile_radar.cgi
#   Copyright 2010 by Ben Cotton
#   <bcotton@funnelfiasco.com>
#   Licensed under the GNU General Public License v2
#
#  This CGI is a wrapper to provide more friendly navigation
# for the National Weather Service mobile weather radar images.
#
# Some code contributed by Mike Kruze, for which I am very grateful.
#
###################

use strict;
use CGI qw/:all/;
use LWP::Simple qw(!head);
use HTTP::Status;


###
#
# Configuration section
#
##

# Contact e-mail to display
my $contactEmail = 'webmaster@example.com';

# The name of the site (to use in the title and header)
my $siteName = 'Funnel Fiasco mobile radar';

# System path to store mirrored images
my $imageRepo = '/var/www/html/nws_mobile';

# Web path to the stored images
my $repoURL = '/nws_mobile';

# URL to point users to if they want to visit your site
my $siteURL = 'http://weather.funnelfiasco.com/mobile';

###
#
# end configuration section
#
##

# version
my $version = '1.0';

# What's my name? This is useful for the self-referencing links below that 
# aren't quite self-referencing.
my $self = 'nws_mobile_radar.cgi';

# Various information about the products.  The first field is the
# plain-text description. The second is the URL (use ^S for the site
# ID and it will get replaced with the ID later).
my $baseURL = 'http://radar.weather.gov/ridge';
my %prodInfo = (
  'N0R' => ['Reflectivity', "$baseURL/lite/N0R/^S_0.png"],
  'N0Rloop' => ['Reflectivity loop', "$baseURL/lite/N0R/^S_loop.gif"],
  'N0Rsmall' => ['Reflectivity (small)', "$baseURL/Thumbs/^S_Thumb.gif"],
  'N0Rsmallloop' => ['Reflectivity loop (small)', "$baseURL/Thumbs/^S_loop_tb.gif"],
  'N0V' => ['Velocity', "$baseURL/lite/N0V/^S_0.png"],
  'N0S' => ['Storm-relative motion', "$baseURL/lite/N0S/^S_0.png"]
);

# The radar sites to use.  I initially left this out, but it's actually a darn
# useful feature.  
my %siteInfo = (
  #Site     Name	        	  NW     N      NE     W      E      SW     S      NW
  'ABC' => ['BETHEL , AK',        '',    'AEC', 'APD', '',    'AHG', '',    '',    'AKC' ],
  'ACG' => ['SITKA, AK',          'APD', '',    '',    'AIH', '',    '',    '',    ''    ],
  'AEC' => ['NOME , AK',          '',    '',    '',    '',    'APD', '',    'ABC', 'AHG' ],
  'AHG' => ['ANCHORAGE, AK',      'AEC', 'APD', '',    'ABC', '',    'AKC', '',    'AIH' ],
  'AIH' => ['MIDDLETON ISL, AK',  'AHG', 'APD', '',    'AKC', '',    '',    '',    'ACG' ],
  'AKC' => ['KING SALMON , AK',   'ABC', '',    'AHG', '',    'AIH', '',    '',    ''    ],
  'APD' => ['FAIRBANKS , AK',     '',    '',    '',    'AEC', '',    'ABC', 'AHG', 'ACG' ],
  'BMX' => ['BIRMINGHAM, AL',     'GWX', 'OHX', 'HTX', 'DGX', 'FFC', 'MOB', 'EVX', 'MXX' ],
  'EOX' => ['FORT RUCKER , AL',   'BMX', 'MXX', 'JGX', 'DGX', 'VAX', 'MOB', 'EVX', 'TLH' ],
  'HTX' => ['HUNTSVILLE, AL',     'HPX', 'OHX', 'MRX', 'NQA', 'GSP', 'GWX', 'BMX', 'FFC' ],
  'MOB' => ['MOBILE , AL',        'DGX', 'GWX', 'EOX', 'POE', 'EVX', 'LIX', '',    ''    ],
  'MXX' => ['CARRVILLE, AL',      'BMX', 'HTX', 'FFC', 'DGX', 'JGX', 'EVX', 'EOX', 'TLH' ],
  'LZK' => ['LITTLE ROCK, AR',    'SRX', 'SGF', 'NQA', 'TLX', 'GWX', 'FWS', 'SHV', 'DGX' ],
  'SRX' => ['SLATINGTON MOU, AR', 'INX', 'SGF', 'NQA', 'TLX', 'LZK', 'FDR', 'FWS', 'SHV' ],
  'EMX' => ['TUCSON, AZ',         '',    'IWA', 'HDX', 'YUX', 'EPZ', '',    '',    ''    ],
  'FSX' => ['FLAGSTAFF, AZ',      '',    'ICX', 'GJX', 'ESX', 'ABX', '',    'IWA', 'HDX' ],
  'IWA' => ['PHOENIX/MESA , AZ',  'ESX', 'FSX', 'ABX', 'SOX', 'HDX', 'YUX', 'EMX', 'EPZ' ],
  'YUX' => ['YUMA , AZ',          'EYX', 'ESX', 'IWA', 'NKX', 'EMX', '',    '',    ''    ],
  'BBX' => ['MARYSVILLE, CA',     '',    'MAX', '',    'BHX', 'RGX', '',    'DAX', ''    ],
  'BHX' => ['EUREKA, CA',         '',    '',    'MAX', '',    'BBX', '',    'MUX', 'DAX' ],
  'DAX' => ['SACRAMENTO , CA',    'BHX', 'BBX', 'RGX', '',    '',    'MUX', 'VBX', 'HNX' ],
  'EYX' => ['EDWARDS AFB , CA',   'HNX', '',    'ESX', 'VBX', '',    'VTX', 'SOX', 'YUX' ],
  'HNX' => ['SAN JOAQUIN VA, CA', 'DAX', 'RGX', 'LRX', 'MUX', 'ESX', 'VBX', 'VTX', 'EYX' ],
  'MUX' => ['SAN FRANCISCO, CA',  '',    'BHX', 'DAX', '',    'HNX', '',    '',    'VBX' ],
  'NKX' => ['SAN DIEGO, CA',      'SOX', '',    '',    '',    'YUX', '',    '',    ''    ],
  'SOX' => ['SANTA ANA, CA',      'VTX', 'EYX', 'ESX', '',    'IWA', '',    '',    'NKX' ],
  'VBX' => ['LOMPOC, CA',         'MUX', 'DAX', 'HNX', '',    'EYX', '',    '',    'VTX' ],
  'VTX' => ['LOS ANGELES, CA',    'VBX', 'HNX', 'EYX', '',    '',    '',    '',    'SOX' ],
  'FTG' => ['DENVER/BOULDER, CO', 'RIW', 'CYS', 'LNX', 'GJX', 'GLD', 'ABX', 'PUX', 'DDC' ],
  'GJX' => ['GRAND JUNCTION, CO', 'MTX', 'RIW', 'CYS', 'ICX', 'FTG', 'FSX', 'ABX', 'PUX' ],
  'PUX' => ['PUEBLO , CO',        '',    'FTG', 'GLD', 'GJX', 'DDC', '',    'ABX', 'AMA' ],
  'DOX' => ['DOVER AFB , DE',     '',    'DIX', '',    'LWX', '',    'AKQ', '',    ''    ],
  'AMX' => ['MIAMI , FL',         'TBW', 'MLB', '',    '',    '',    '',    'BYX', 'JUA' ],
  'BYX' => ['KEY WEST , FL',      'TLH', 'TBW', 'MLB', '',    'AMX', '',    'GMO', 'JUA' ],
  'EVX' => ['RED BAY , FL',       'DGX', 'MXX', 'EOX', 'MOB', 'TLH', '',    'BYX', 'TBW' ],
  'JAX' => ['JACKSONVILLE , FL',  'VAX', 'CLX', '',    'TLH', '',    'TBW', 'MLB', ''    ],
  'MLB' => ['MELBOURNE , FL',     'TLH', 'JAX', 'CLX', 'TBW', '',    'BYX', 'AMX', ''    ],
  'TBW' => ['TAMPA, FL',          'EVX', 'TLH', 'JAX', '',    'MLB', '',    'BYX', 'AMX' ],
  'TLH' => ['TALLAHASSEE , FL',   'EOX', 'JGX', 'VAX', 'EVX', 'JAX', 'BYX', 'TBW', 'MLB' ],
  'FFC' => ['ATLANTA, GA',        'HTX', 'MRX', 'GSP', 'BMX', 'CAE', 'EOX', 'JGX', 'CLX' ],
  'JGX' => ['WARNER ROBINS, GA',  'FFC', 'GSP', 'CAE', 'BMX', 'CLX', 'MXX', 'VAX', 'JAX' ],
  'VAX' => ['VALDOSTA, GA',       'MXX', 'JGX', 'CLX', 'EOX', 'JAX', 'TLH', 'TBW', 'MLB' ],
  'HKI' => ['SOUTH KAUAI',        '',    '',    '',    '',    '',    '',    '',    'HMO' ],
  'HKM' => ['KAMUELA, HI',        'HMO', '',    '',    '',    '',    '',    'HWA', ''    ],
  'HMO' => ['MOLOKAI, HI',        'HKI', '',    '',    '',    '',    '',    '',    'HKM' ],
  'HWA' => ['SOUTH HAWAII, HI',   '',    'HKM', '',    '',    '',    '',    '',    ''    ],
  'DMX' => ['DES MOINES, IA',     'FSD', 'MPX', 'ARX', 'OAX', 'DVN', 'TWX', 'EAX', 'ILX' ],
  'DVN' => ['DAVENPORT, IA',      'MPX', 'ARX', 'MKX', 'DMX', 'LOT', 'EAX', 'LSX', 'ILX' ],
  'CBX' => ['BOISE, ID',          'PDT', 'MSX', 'TFX', 'MAX', 'SFX', 'RGX', 'LRX', 'MTX' ],
  'SFX' => ['POCATELLO, ID',      'MSX', 'TFX', 'BLX', 'CBX', 'RIW', 'LRX', 'MTX', ''    ],
  'ILX' => ['LINCOLN , IL',       'DVN', 'MKX', 'LOT', 'DMX', 'IND', 'LSX', 'PAH', 'VWX' ],
  'LOT' => ['CHICAGO, IL',        'ARX', 'MKX', 'GRR', 'DVN', 'IWX', 'LSX', 'ILX', 'IND' ],
  'IND' => ['INDIANAPOLIS , IN',  'LOT', 'IWX', 'DTX', 'ILX', 'ILN', 'VWX', 'LVX', 'JKL' ],
  'IWX' => ['NORTH WEBSTER , IN', 'MKX', 'GRR', 'DTX', 'LOT', 'CLE', 'ILX', 'IND', 'ILN' ],
  'DDC' => ['DODGE CITY , KS',    'GLD', 'UEX', 'TWX', 'PUX', 'ICT', 'AMA', 'VNX', 'TLX' ],
  'GLD' => ['GOODLAND , KS',      'CYS', 'LNX', 'UEX', 'FTG', 'TWX', 'PUX', 'AMA', 'DDC' ],
  'ICT' => ['WICHITA , KS',       'GLD', 'UEX', 'TWX', 'DDC', 'SGF', 'VNX', 'TLX', 'INX' ],
  'TWX' => ['TOPEKA, KS',         'UEX', 'OAX', 'DMX', 'GLD', 'EAX', 'DDC', 'ICT', 'SGF' ],
  'HPX' => ['FORT CAMPBELL , KY', 'LSX', 'VWX', 'LVX', 'PAH', 'JKL', 'NQA', 'OHX', 'MRX' ],
  'JKL' => ['JACKSON, KY'       , 'IND', 'ILN', 'RLX', 'LVX', 'FCX', 'OHX', 'MRX', 'GSP' ],
  'LVX' => ['LOUISVILLE, KY',     'ILX', 'IND', 'ILN', 'VWX', 'JKL', 'PAH', 'OHX', 'MRX' ],
  'PAH' => ['PADUCAH , KY',       'LSX', 'ILX', 'VWX', 'SGF', 'LVX', 'LZK', 'NQA', 'HPX' ],
  'LCH' => ['LAKE CHARLES , LA',  'FWS', 'POE', 'DGX', 'GRK', 'LIX', 'HGX', '',    ''    ],
  'LIX' => ['NEW ORLEANS, LA',    'SHV', 'DGX', 'MXX', 'POE', 'MOB', 'LCH', '',    ''    ],
  'POE' => ['FORT POLK , LA',     'FWS', 'SHV', 'DGX', 'GRK', 'MOB', 'HGX', 'LCH', 'LIX' ],
  'SHV' => ['SHREVEPORT , LA',    'TLX', 'SRX', 'LZK', 'FWS', 'DGX', 'HGX', 'LCH', 'LIX' ],
  'BOX' => ['BOSTON, MA',         'CXX', 'GYX', '',    'ENX', '',    'OKX', '',    ''    ],
  'CBW' => ['CARIBOU, ME',        '',    '',    '',    'CXX', '',    'GYX', '',    ''    ],
  'GYX' => ['PORTLAND, ME',       '',    '',    'CBW', 'CXX', '',    'ENX', 'BOX', ''    ],
  'APX' => ['GAYLORD , MI',       'MQT', '',    '',    'GRB', '',    'MKX', 'GRR', 'DTX' ],
  'DTX' => ['DETROIT, MI',        'GRB', 'APX', '',    'GRR', 'BUF', 'IWX', 'ILN', 'CLE' ],
  'GRR' => ['GRAND RAPIDS , MI',  'GRB', 'APX', 'BUF', 'MKX', 'DTX', 'LOT', 'IWX', 'CLE' ],
  'MQT' => ['MARQUETTE, MI',      '',    '',    '',    'DLH', '',    'MPX', 'GRB', 'APX' ],
  'DLH' => ['DULUTH , MN',        'MVX', '',    '',    '',    'MQT', 'MPX', 'ARX', 'GRB' ],
  'MPX' => ['MINNEAPOLIS, MN',    'MVX', 'DLH', 'MQT', 'ABR', 'GRB', 'FSD', 'DMX', 'ARX' ],
  'EAX' => ['KANSAS CITY, MO',    'OAX', 'DMX', 'DVN', 'TWX', 'LSX', 'ICT', 'SGF', 'PAH' ],
  'LSX' => ['ST. LOUIS, MO',      'DMX', 'DVN', 'ILX', 'EAX', 'VWX', 'SGF', 'LZK', 'PAH' ],
  'SGF' => ['SPRINGFIELD , MO',   'TWX', 'EAX', 'LSX', 'ICT', 'PAH', 'INX', 'LZK', 'NQA' ],
  'GWX' => ['COLUMBUS AFB , MS',  'NQA', 'HPX', 'OHX', 'LZK', 'HTX', 'DGX', 'MOB', 'BMX' ],
  'DGX' => ['JACKSON , MS',       'LZK', 'NQA', 'GWX', 'SHV', 'BMX', 'POE', 'LIX', 'MOB' ],
  'BLX' => ['BILLINGS, MT',       'TFX', 'GGW', 'MBX', '',    'BIS', 'SFX', 'RIW', 'UDX' ],
  'GGW' => ['GLASGOW , MT',       '',    '',    '',    'TFX', 'MBX', '',    'BLX', 'BIS' ],
  'MSX' => ['MISSOULA, MT',       '',    '',    '',    'OTX', 'TFX', 'PDT', 'CBX', 'SFX' ],
  'TFX' => ['GREAT FALLS , MT',   '',    '',    '',    'MSX', 'GGW', 'CBX', 'SFX', 'BLX' ],
  'LTX' => ['WILMINGTON, NC',     'GSP', 'RAX', 'MHX', 'CAE', '',    'CLX', '',    ''    ],
  'MHX' => ['MOREHEAD CITY, NC',  'FCX', 'AKQ', '',    'RAX', '',    'LTX', '',    ''    ],
  'RAX' => ['RALEIGH-DURHAM, NC', 'FCX', 'LWX', 'AKQ', 'MRX', 'MHX', 'GSP', 'CAE', 'LTX' ],
  'BIS' => ['BISMARCK , ND',      'GGW', 'MBX', 'MVX', 'BLX', '',    'UDX', '',    'ABR' ],
  'MBX' => ['MINOT AFB , ND',     '',    '',    '',    'GGW', 'MVX', 'BLX', 'BIS', 'ABR' ],
  'MVX' => ['FARGO, ND',          '',    '',    '',    'MBX', 'DLH', 'BIS', 'ABR', 'MPX' ],
  'LNX' => ['NORTH PLATTE, NE',   'UDX', 'ABR', 'FSD', 'CYS', 'OAX', 'FTG', 'GLD', 'UEX' ],
  'OAX' => ['OMAHA, NE',          '',    'FSD', 'MPX', 'LNX', 'DMX', 'UEX', 'TWX', 'EAX' ],
  'UEX' => ['HASTINGS, NE',       'LNX', '',    'FSD', 'GLD', 'OAX', 'DDC', 'ICT', 'TWX' ],
  'ABX' => ['ALBUQUERQUE , NM',   'ICX', 'GJX', 'PUX', 'FSX', 'AMA', 'EMX', 'HDX', 'FDX' ],
  'FDX' => ['CLOVIS , NM',        'ABX', 'PUX', 'DDC', 'HDX', 'AMA', 'EPZ', 'MAF', 'LBB' ],
  'HDX' => ['ALAMOGORDO, NM',     'FSX', 'ABX', 'FDX', 'IWA', 'LBB', 'EMX', 'EPZ', 'MAF' ],
  'ESX' => ['LAS VEGAS, NV',      'RGX', 'LRX', 'ICX', 'HNX', 'FSX', 'EYX', 'YUX', 'IWA' ],
  'LRX' => ['ELKO, NV',            '',   'CBX', 'SFX', 'RGX', 'MTX', 'HNX', 'ESX', 'ICX' ],
  'RGX' => ['RENO, NV',           'MAX', 'PDT', 'CBX', 'BBX', 'LRX', 'DAX', 'HNX', 'ESX' ],
  'BGM' => ['BINGHAMTON , NY',    '',    'TYX', 'ENX', 'BUF', 'OKX', 'PBZ', 'CCX', 'DIX' ],
  'BUF' => ['BUFFALO, NY',        'APX', '',    'TYX', 'DTX', 'BGM', 'CLE', 'PBZ', 'CCX' ],
  'ENX' => ['ALBANY, NY',         'TYX', 'CXX', 'GYX', 'BUF', 'BOX', 'BGM', '',    'OKX' ],
  'OKX' => ['NEW YORK CITY, NY',  'BGM', 'ENX', 'BOX', 'CCX', '',    'DIX', '',    ''    ],
  'CLE' => ['CLEVELAND , OH',     'DTX', '',    'BUF', 'IWX', 'CCX', 'ILN', 'RLX', 'PBZ' ],
  'ILN' => ['CINCINNATI, OH',     'IWX', 'DTX', 'CLE', 'IND', 'PBZ', 'LVX', 'JKL', 'RLX' ],
  'FDR' => ['FREDERICK, OK',      'AMA', 'DDC', 'VNX', 'FDX', 'TLX', 'LBB', 'DYX', 'FWS' ],
  'INX' => ['TULSA , OK',         'VNX', 'ICT', 'SGF', 'TLX', 'SRX', 'FDR', 'FWS', 'SHV' ],
  'TLX' => ['OKLAHOMA CITY, OK',  'VNX', 'ICT', 'INX', 'AMA', 'SRX', 'FDR', 'FWS', 'SHV' ],
  'VNX' => ['ENID, OK',           'DDC', 'ICT', 'SGF', 'PUX', 'INX', 'AMA', 'FDR', 'TLX' ],
  'MAX' => ['MEDFORD, OR',        '',    'RTX', 'PDT', '',    'CBX', 'BHX', 'BBX', 'RGX' ],
  'PDT' => ['PENDLETON , OR',     'ATX', 'OTX', 'MSX', 'RTX', '',    'MAX', 'RGX', 'CBX' ],
  'RTX' => ['PORTLAND, OR',       '',    'ATX', 'OTX', '',    'PDT', '',    'MAX', ''    ],
  'CCX' => ['STATE COLLEGE, PA',  'BUF', 'BUF', 'BGM', 'CLE', 'OKX', 'PBZ', 'LWX', 'DIX' ],
  'DIX' => ['PHILADELPHIA , PA',  'CCX', 'ENX', 'OKX', 'PBZ', '',    'LWX', 'DOX', ''    ],
  'PBZ' => ['PITTSBURGH, PA',     'CLE', 'BUF', 'BGM', 'ILN', 'CCX', 'RLX', 'FCX', 'LWX' ],
  'JUA' => ['SAN JUAN, PR',       'AMX', '',    '',    'BYX', '',    'GMO', '',    ''    ],
  'CAE' => ['COLUMBIA , SC',      'GSP', 'FCX', 'RAX', 'FFC', 'LTX', 'JGX', 'CLX', ''    ],
  'CLX' => ['CHARLESTON, SC',     'GSP', 'CAE', 'LTX', 'JGX', '',    'VAX', 'JAX', ''    ],
  'GSP' => ['GREENVILLE, SC',     'MRX', 'RLX', 'FCX', 'OHX', 'RAX', 'HTX', 'FFC', 'CAE' ],
  'ABR' => ['ABERDEEN , SD',      'BIS', 'MVX', 'DLH', '',    'MPX', 'UDX', 'LNX', 'FSD' ],
  'FSD' => ['SIOUX FALLS , SD',   'ABR', 'MVX', 'MPX', 'UDX', 'ARX', 'LNX', 'OAX', 'DMX' ],
  'UDX' => ['RAPID CITY, SD',     'BLX', 'BIS', 'ABR', 'RIW', 'FSD', 'CYS', 'LNX', ''    ],
  'MRX' => ['KNOXVILLE, TN',      'HPX', 'JKL', 'FCX', 'OHX', 'RAX', 'HTX', 'FFC', 'GSP' ],
  'NQA' => ['MEMPHIS, TN',        'SGF', 'PAH', 'HPX', 'SRX', 'OHX', 'LZK', 'GWX', 'HTX' ],
  'OHX' => ['NASHVILLE, TN',      'PAH', 'HPX', 'JKL', 'NQA', 'MRX', 'GWX', 'HTX', 'GSP' ],
  'AMA' => ['AMARILLO , TX',      'PUX', 'DDC', 'VNX', 'ABX', 'FDR', 'FDX', 'LBB', 'DYX' ],
  'BRO' => ['BROWNSVILLE , TX',   'DFX', 'CRP', 'HGX', '',    '',    '',    '',    ''    ],
  'CRP' => ['CORPUS CHRISTI, TX', 'SJT', 'EWX', 'HGX', 'DFX', '',    '',    'BRO', ''    ],
  'DFX' => ['DEL RIO, TX',        'MAF', 'SJT', 'GRK', '',    'EWX', '',    '',    'CRP' ],
  'DYX' => ['ABILENE, TX',        'LBB', 'FDR', '',    '',    'FWS', 'MAF', 'SJT', 'GRK' ],
  'EPZ' => ['EL PASO , TX',       'FSX', 'ABX', 'HDX', 'EMX', 'MAF', '',    '',    'DFX' ],
  'EWX' => ['AUSTIN, TX',         'SJT', 'FWS', 'GRK', 'DFX', 'HGX', '',    'BRO', 'CRP' ],
  'FWS' => ['DALLAS-FT WORTH, TX', 'FDR', 'TLX', 'LZK', 'DYX', 'SHV', 'SJT', 'GRK', 'POE' ],
  'GRK' => ['KILLEEN, TX',        'DYX', 'FWS', 'SHV', 'SJT', 'POE', 'EWX', 'CRP', 'HGX' ],
  'HGX' => ['HOUSTON, TX',        'GRK', 'FWS', 'POE', 'EWX', 'LCH', 'CRP', 'BRO', ''    ],
  'LBB' => ['LUBBOCK , TX',       'FDX', 'AMA', 'FDR', 'HDX', 'DYX', 'EPZ', 'MAF', 'SJT' ],
  'MAF' => ['MIDLAND, TX',        'HDX', 'LBB', 'DYX', 'EPZ', 'SJT', '',    '',    'DFX' ],
  'SJT' => ['SAN ANGELO , TX',    'LBB', 'DYX', 'FWS', 'MAF', 'GRK', '',    'DFX', 'EWX' ],
  'ICX' => ['CEDAR CITY , UT',    'LRX', 'MTX', '',    '',    'GJX', 'ESX', 'FSX', 'ABX' ],
  'MTX' => ['SALT LAKE CITY, UT', 'CBX', 'SFX', 'RIW', 'LRX', 'CYS', '',    'ICX', 'GJX' ],
  'AKQ' => ['NORFOLK, VA',        'LWX', 'DOX', '',    'FCX', '',    'RAX', 'MHX', ''    ],
  'FCX' => ['ROANOKE, VA',        'RLX', 'PBZ', 'LWX', 'MRX', 'AKQ', 'GSP', 'CAE', 'RAX' ],
  'LWX' => ['STERLING , VA',      'PBZ', 'CCX', 'DIX', 'FCX', 'DOX', 'RAX', 'AKQ', ''    ],
  'CXX' => ['BURLINGTON, VT',     '',    '',    'CBW', 'TYX', 'GYX', 'BGM', 'ENX', 'BOX' ],
  'ATX' => ['SEATTLE-TACOMA, WA', '',    '',    '',    '',    'OTX', '',    'RTX', 'PDT' ],
  'OTX' => ['SPOKANE , WA',       '',    '',    '',    'ATX', 'MSX', 'RTX', 'PDT', ''    ],
  'ARX' => ['LA CROSSE , WI',     'MPX', 'DLH', 'MQT', 'FSD', 'GRB', 'DMX', 'DVN', 'MKX' ],
  'GRB' => ['GREEN BAY, WI',      'DLH', 'MQT', '',    'MPX', 'APX', 'ARX', 'MKX', 'GRR' ],
  'MKX' => ['MILWAUKEE, WI',      'ARX', 'GRB', 'APX', 'DMX', 'GRR', 'DVN', 'LOT', 'IWX' ],
  'RLX' => ['CHARLESTON, WV',     'ILN', 'CLE', 'PBZ', 'LVX', 'LWX', 'JKL', 'GSP', 'FCX' ],
  'CYS' => ['CHEYENNE , WY',      'BLX', 'UDX', 'ABR', 'RIW', 'LNX', 'GJX', 'FTG', 'GLD' ],
  'RIW' => ['RIVERTON , WY',      '',    'BLX', '',    'SFX', 'UDX', 'MTX', 'GJX', 'CYS' ],
);

# Give the directions numbers to match their dial sites
my @directions = ( 'empty', 'NW', 'N', 'NE', 'W', 'E', 'SW', 'S', 'SE' );

my @products = keys(%prodInfo);
my @sites = keys(%siteInfo);

# grab the CGI input
my $query = new CGI();

# Before we go any further, it's a good idea to print the usual
# CGI stuff.
print header;

# Print the page title and a header
print start_html("$siteName"), h2("$siteName"), "<hr>";

# Grab the product type we're interested in 
my $prodType = $query->param('prodType');

if ( $prodType eq '' ) {
  &printMenu;
} else {
  &showRadar($prodType);
}

print "<hr>This service is experimental and should not be used for operational purposes. Data provided by the National Weather Service. For more information visit <a href=\"$siteURL\">$siteURL</a> or e-mail <a href=\"mailto:$contactEmail\">$contactEmail</a>.<br>nws_mobile_radar.cgi $version copyright 2012 by Ben Cotton. Licensed under GPL v2"; 

# close out the HTML
print $query->end_html;


#########
#
# printMenu subroutine
#     Displays a menu for users to choose the radar product they want.
#
#########

sub printMenu {

  #Define what gets used in the popup menus
  my @valuesSite = ( 'textentry' );
  my %labelsSite;
  $labelsSite{'textentry'} = 'Manual text entry -->';
  my @valuesProd;
  my %labelsProd;

  foreach (sort (@sites)) {
    push(@valuesSite, $_);
	$labelsSite{$_} = "$_ - $siteInfo{$_}[0]";
  }
  foreach (@products) {
    push(@valuesProd, $_);
    $labelsProd{$_} = $prodInfo{$_}[0];
  }

   print start_form,
    "Select a site or enter a 3-character site ID and select image type<br>",
    popup_menu(-name=>'siteIDdrop',
				-values=>\@valuesSite,
				default=>'textentry',
				-labels=>\%labelsSite),
    '&nbsp;&nbsp;',
	textfield(-name=>'siteIDtext',-size=>3,-maxlength=>3),
    '<br>',
    popup_menu(-name=>'prodType',
                -values=>\@valuesProd,
               default=>'N0R',
                -labels=>\%labelsProd),
     '&nbsp;&nbsp;',
     submit;

}

#########
#
# showRadar subroutine
#    Mirror the radar image from the NWS and present it to the user
#
#########

sub showRadar {

   # What's the station ID we're after?  
   my $siteID = $query->param('siteIDdrop');
   if ( $siteID eq 'textentry' ) { $siteID = $query->param('siteIDtext'); }

   # Capitalize the site ID. The downloading seems case-insensitive, but the
   # local caching sure isn't!
   $siteID =~ tr/[a-z]/[A-Z]/;
   
   print h3("$siteInfo{$siteID}[0] ($siteID) $prodInfo{$prodType}[0]");

   my $imageURL = $prodInfo{$prodType}[1];
   $imageURL =~ s/\^S/$siteID/g;

  # Mirror the image
  mirror("$imageURL", "$imageRepo/radar_mirror-$siteID-$prodType.gif");

  # Set up the click to reload functionality
  print "<a href=\"", self_url, "\">"; 
  
  print img {src=>"$repoURL/radar_mirror-$siteID-$prodType.gif"}, "</a>", br;
  print "Click image to reload", br br, '|';

  # Give quick options to other images, since that's what the NWS site lacks
  foreach (@products) {
    unless ( "$_" eq "$prodType" ) {
      print "<a href=\"$self?siteIDdrop=$siteID&prodType=$_\">$prodInfo{$_}[0]</a>&nbsp;|&nbsp;";
    }
  }

  # Produce the dial for selecting adjacent sites
  print br br, "Adjacent sites", br;

  # Make the table. I don't use the functions provided by CGI.pm and instead
  # write the HTML by hand because I think it makes the code a bit cleaner.
  print "<table border=\"1\">\n<tr>\n";
  
  for ( my $dialCounter = 1; $dialCounter <= 8; $dialCounter++ ) {
    if ( ( $dialCounter == 1 ) || ( $dialCounter == 4 ) || ( $dialCounter == 6 ) ) {
      print "<tr>"; 
      }

    print "<td align=\"center\">$directions[$dialCounter] - ";
    unless ( $siteInfo{$siteID}[$dialCounter] eq "" ) { 
      print "<a href=\"$self?siteIDdrop=$siteInfo{$siteID}[$dialCounter]&prodType=$prodType\">";
      print "$siteInfo{$siteID}[$dialCounter]</a></td>";
    } 

    if ( $dialCounter == 4 ) { 
      print "<td></td>"; 
    }

    if ( ( $dialCounter == 3 ) || ( $dialCounter == 5 ) || ( $dialCounter == 8 ) ) {
      print "</tr>";
    }

  } 

  print "</table>";

  print br, "<a href=\"$self\">Select another site</a>";

  print br br, "<a href=\"http://mobile.srh.noaa.gov\">NWS mobile site</a>";
}
