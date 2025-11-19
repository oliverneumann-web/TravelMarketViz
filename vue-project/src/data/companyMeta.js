const logoPath = (fileName) => new URL(`../logos/${fileName}`, import.meta.url).href

export const companyMeta = {
  ABNB: {
    name: 'Airbnb',
    color: '#ff5895',
    logo: logoPath('ABNB_logo.png'),
  },
  Almosafer: {
    name: 'Almosafer',
    color: '#bb5387',
    logo: logoPath('Almosafer_logo.png'),
  },
  BKNG: {
    name: 'Booking.com',
    color: '#003480',
    logo: logoPath('BKNG_logo.png'),
  },
  DESP: {
    name: 'Despegar',
    color: '#755bd8',
    logo: logoPath('DESP_logo.png'),
  },
  EXPE: {
    name: 'Expedia',
    color: '#fbcc33',
    logo: logoPath('EXPE_logo.png'),
  },
  EaseMyTrip: {
    name: 'EaseMyTrip',
    color: '#00a0e2',
    logo: logoPath('EASEMYTRIP_logo.png'),
  },
  Ixigo: {
    name: 'Ixigo',
    color: '#e74c3c',
    logo: logoPath('IXIGO_logo.png'),
  },
  MMYT: {
    name: 'MakeMyTrip',
    color: '#e74c3c',
    logo: logoPath('MMYT_logo.png'),
  },
  TRIP: {
    name: 'TripAdvisor',
    color: '#00af87',
    logo: logoPath('TRIP_logo.png'),
  },
  TRVG: {
    name: 'Trivago',
    color: '#e74c3c',
    logo: logoPath('TRVG_logo.png'),
  },
  Wego: {
    name: 'Wego',
    color: '#4e843d',
    logo: logoPath('Wego_logo.png'),
  },
  Yatra: {
    name: 'Yatra.com',
    color: '#e74c3c',
    logo: logoPath('YTRA_logo.png'),
  },
  TCOM: {
    name: 'Trip.com',
    color: '#2577e3',
    logo: logoPath('TCOM_logo.png'),
  },
  EDR: {
    name: 'Edreams',
    color: '#2577e3',
    logo: logoPath('EDR_logo.png'),
  },
  LMN: {
    name: 'Lastminute',
    color: '#fc03b1',
    logo: logoPath('LMN_logo.png'),
  },
  Webjet: {
    name: 'Webjet',
    color: '#e74c3c',
    logo: logoPath('WEB_logo.png'),
  },
  SEERA: {
    name: 'Seera Group',
    color: '#750808',
    logo: logoPath('SEERA_logo.png'),
  },
  PCLN: {
    name: 'Priceline',
    color: '#003480',
    logo: logoPath('PCLN_logo.png'),
  },
  Orbitz: {
    name: 'Orbitz',
    color: '#8edbfa',
    logo: logoPath('OWW_logo.png'),
  },
  Travelocity: {
    name: 'Travelocity',
    color: '#1d3e5c',
    logo: logoPath('Travelocity_logo.png'),
  },
  Skyscanner: {
    name: 'Skyscanner',
    color: '#0770e3',
    logo: logoPath('Skyscanner_logo.png'),
  },
  Etraveli: {
    name: 'Etraveli',
    color: '#b2e9ff',
    logo: logoPath('Etraveli_logo.png'),
  },
  Kiwi: {
    name: 'Kiwi',
    color: '#e5fdd4',
    logo: logoPath('Kiwi_logo.png'),
  },
  Cleartrip: {
    name: 'Cleartrip',
    color: '#e74c3c',
    logo: logoPath('Cleartrip_logo.png'),
  },
  Traveloka: {
    name: 'Traveloka',
    color: '#38a0e2',
    logo: logoPath('Traveloka_logo.png'),
  },
  FLT: {
    name: 'Flight Centre',
    color: '#d2b6a8',
    logo: logoPath('FlightCentre_logo.png'),
  },
  'Webjet OTA': {
    name: 'Webjet OTA',
    color: '#e74c3c',
    logo: logoPath('OTA_logo.png'),
  },
  KYAK: {
    name: 'Kayak',
    color: '#ff690f',
    logo: logoPath('KYAK_logo.png'),
  },
  eLong: {
    name: 'eLong',
    color: '#2141b2',
    logo: logoPath('ELONG_logo.png'),
  },
  'Tongcheng Travel': {
    name: 'Tongcheng Travel',
    color: '#5b318f',
    logo: logoPath('Tongcheng_logo.png'),
  },
  'Tongcheng': {
    note: 'Same as Tongcheng Travel',
    name: 'Tongcheng Travel',
    color: '#5b318f',
    logo: logoPath('Tongcheng_logo.png'),
  },
  eSky: {
    name: 'eSky',
    color: '#002071',
    logo: logoPath('eSky_logo.png'),
  },
};

export const companyNames = Object.fromEntries(
  Object.entries(companyMeta).map(([key, value]) => [key, value.name])
);

const DEFAULT_COLOR = '#64748b';

export const getCompanyColor = (key) => companyMeta[key]?.color ?? DEFAULT_COLOR;
export const getCompanyLogo = (key) => companyMeta[key]?.logo ?? '';

