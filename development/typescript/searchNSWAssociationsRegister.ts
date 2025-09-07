// import axios, { AxiosResponse } from 'axios';
// import * as cheerio from 'cheerio';
// import { setTimeout } from 'timers';

// interface SearchResult {
//   incorporation_number: string;
//   name: string;
//   suburb: string;
//   postcode: string;
//   status: string;
//   date_of_incorporation: string;
// }

// interface PaginationTarget {
//   page_num: number;
//   event_arg: string;
// }

// class Session {
//   private headers: Record<string, string>;
//   private cookies: Record<string, string>;
//   private auth: string | null;
//   private proxies: Record<string, string>;
//   private hooks: Record<string, Function>;
//   private params: Record<string, string>;
//   private stream: boolean;
//   private verify: boolean;
//   private cert: string | null;
//   private maxRedirects: number;
//   private trust_env: boolean;

//   constructor() {
//     this.headers = {
//       'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
//       'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
//       'X-Requested-With': 'XMLHttpRequest'
//     };
//     this.cookies = {};
//     this.auth = null;
//     this.proxies = {};
//     this.hooks = {};
//     this.params = {};
//     this.stream = false;
//     this.verify = true;
//     this.cert = null;
//     this.maxRedirects = 30;
//     this.trust_env = true;
//     this.cookies = {};
//   }

//   async request(method: string, url: string, data?: Record<string, string>, json?: any): Promise<AxiosResponse> {
//     const config: any = {
//       headers: this.headers,
//       params: this.params,
//       auth: this.auth,
//       cookies: this.cookies,
//       hooks: this.hooks,
//       timeout: 0,
//       allowRedirects: true,
//       maxRedirects: this.maxRedirects,
//       verify: this.verify,
//       cert: this.cert,
//       proxy: this.proxies,
//       responseType: 'stream' || this.stream ? 'stream' : undefined
//     };

//     if (data) {
//       config.data = data;
//     }
//     if (json) {
//       config.json = json;
//     }

//     const response = await axios({
//       method,
//       url,
//       ...config
//     });

//     return response;
//   }

//   async get(url: string, params?: Record<string, string>): Promise<AxiosResponse> {
//     return this.request('GET', url, undefined, undefined, params);
//   }

//   async post(url: string, data?: Record<string, string>, json?: any): Promise<AxiosResponse> {
//     return this.request('POST', url, data, json);
//   }

//   async scrapeWebsite(suburb: string = 'RYDE', state: string = 'NSW', postcode: string = '2729', delay: number = 1): Promise<SearchResult[] | null> {
//     const url = 'https://applications.fairtrading.nsw.gov.au/assocregister/default.aspx';
//     const session = new this.constructor();

//     try {
//       // Initial GET request
//       const initialResponse = await session.get(url, { headers: session.headers });
//       initialResponse.raiseForStatus();

//       const $ = cheerio.load(initialResponse.data);

//       const payload: Record<string, string> = {
//         'ctl00$ScriptManager1': 'ctl00$MainArea$AdvancedSearchSection$updatePanelMain|ctl00$MainArea$AdvancedSearchSection$AdvancedSearchButton',
//         'ctl00$MainArea$AdvancedSearchSection$Assocationname': '',
//         'ctl00$MainArea$AdvancedSearchSection$Associationstatus': '',
//         'ctl00$MainArea$AdvancedSearchSection$Incorporationnumber': '',
//         'ctl00$MainArea$AdvancedSearchSection$Datefromincorporation': '',
//         'ctl00$MainArea$AdvancedSearchSection$DatetoIncorporation': '',
//         'ctl00$MainArea$AdvancedSearchSection$Suburb': suburb,
//         'ctl00$MainArea$AdvancedSearchSection$State': state,
//         'ctl00$MainArea$AdvancedSearchSection$Postcode': postcode,
//         'ctl00$MainArea$AdvancedSearchSection$AssociationSearchGridSortExpression': '',
//         'ctl00$MainArea$AdvancedSearchSection$AssociationSearchGridSortDirection': '',
//         'hiddenInputToUpdateATBuffer_CommonToolkitScripts': '0',
//         '__EVENTTARGET': 'ctl00$MainArea$AdvancedSearchSection$AdvancedSearchButton',
//         '__EVENTARGUMENT': '',
//         '__VIEWSTATE': '',
//         '__VIEWSTATEGENERATOR': '',
//         '__SCROLLPOSITIONX': '0',
//         '__SCROLLPOSITIONY': '0',
//         '__EVENTVALIDATION': '',
//         '__ASYNCPOST': 'true'
//       };

//       // Extract hidden fields
//       const hiddenFields = await this.extractHiddenFields($);

//       payload['__VIEWSTATE'] = hiddenFields['__VIEWSTATE'];
//       payload['__VIEWSTATEGENERATOR'] = hiddenFields['__VIEWSTATEGENERATOR'];
//       payload['__EVENTVALIDATION'] = hiddenFields['__EVENTVALIDATION'];

//       // Send initial POST request
//       const response = await session.post(url, payload, { headers: session.headers });
//       response.raiseForStatus();

//       const content = response.data;

//       // Extract table HTML
//       const tableMatch = content.match(/(<table[^>]*id="MainArea_AdvancedSearchSection_AssociationSearchGrid"[\s\S]*?</table>)/);
//       let $table: cheerio.CheerioAPI;
//       if (tableMatch) {
//         $table = cheerio.load(tableMatch[1]);
//       } else {
//         $table = cheerio.load(content);
//       }

//       const results: SearchResult[] = await this.extractTableResults($table);

//       // Pagination
//       let seenPages = new Set([1]);
//       while (true) {
//         const paginationTargets = await this.extractPaginationTargets($table);
//         const nextPages = paginationTargets.filter(([page_num, event_arg]) => !seenPages.has(page_num));

//         if (nextPages.length === 0) {
//           break;
//         }

//         const [nextPageNum, nextEventArgument] = nextPages[0];
//         seenPages.add(nextPageNum);

//         // Update hidden fields
//         const newHiddenFields = await this.extractHiddenFields($table);
//         payload['__VIEWSTATE'] = newHiddenFields['__VIEWSTATE'];
//         payload['__VIEWSTATEGENERATOR'] = newHiddenFields['__VIEWSTATEGENERATOR'];
//         payload['__EVENTVALIDATION'] = newHiddenFields['__EVENTVALIDATION'];

//         // Send POST request for next page
//         payload['ctl00$ScriptManager1'] = 'ctl00$MainArea$AdvancedSearchSection$ctl08|ctl00$MainArea$AdvancedSearchSection$AssociationSearchGrid';
//         payload['__EVENTTARGET'] = 'ctl00$MainArea$AdvancedSearchSection$AssociationSearchGrid';
//         payload['__EVENTARGUMENT'] = nextEventArgument;
//         payload['__ASYNCPOST'] = 'true';

//         await setTimeout(() => {}, delay);

//         const nextPageResponse = await session.post(url, payload, { headers: session.headers });
//         nextPageResponse.raiseForStatus();

//         const nextPageContent = nextPageResponse.data;

//         if (tableMatch) {
//           $table = cheerio.load(tableMatch[1]);
//         } else {
//           $table = cheerio.load(nextPageContent);
//         }

//         const pageResults = await this.extractTableResults($table);
//         results.push(...pageResults);
//       }

//       return results;
//     } catch (error) {
//       console.error('Scraping error:', error);
//       return null;
//     }
//   }

//   private async extractHiddenFields($: cheerio.CheerioAPI): Promise<Record<string, string>> {
//     const fields: Record<string, string> = {};
//     const patterns: Record<string, RegExp> = {
//       '__VIEWSTATE': /hiddenField|__VIEWSTATE\|([^|]*)\|/,
//       '__EVENTVALIDATION': /hiddenField|__EVENTVALIDATION\|([^|]*)\|/,
//       '__VIEWSTATEGENERATOR': /hiddenField|__VIEWSTATEGENERATOR\|([^|]*)\|/
//     };

//     for (const [field, pattern] of Object.entries(patterns)) {
//       const match = pattern.exec($('body').text());
//       if (match) {
//         fields[field] = match[1];
//       }
//     }

//     return fields;
//   }

//   private async extractTableResults($: cheerio.CheerioAPI): Promise<SearchResult[]> {
//     const results: SearchResult[] = [];

//     const table = $('table#MainArea_AdvancedSearchGrid');
//     if (table.length === 0) {
//       return results;
//     }

//     const rows = table.find('tr').slice(1);

//     for (let i = 0; i < rows.length; i++) {
//       const row = rows[i];
//       if (row.find('table').length > 0) {
//         continue; // Skip pagination row
//       }

//       if (row.find('td').length >= 6) {
//         const incorporationNumber = row.find('a').text().trim() || row.find('td').eq(0).text().trim();
//         results.push({
//           incorporation_number: incorporationNumber,
//           name: row.find('td').eq(1).text().trim() || '',
//           suburb: row.find('td').eq(2).text().trim() || '',
//           postcode: row.find('td').eq(3).text().trim() || '',
//           status: row.find('td').eq(4).text().trim() || '',
//           date_of_incorporation: row.find('td').eq(5).text().trim() || ''
//         });
//       }
//     }

//     return results;
//   }

//   private async extractPaginationTargets($: cheerio.CheerioAPI): Promise<PaginationTarget[]> {
//     const table = $('table#MainArea_AdvancedSearchGrid');
//     if (table.length === 0) {
//       return [];
//     }

//     const paginationTargets: PaginationTarget[] = [];

//     table.find('tr').each((_, tr) => {
//       const aTags = $(tr).find('a');
//       aTags.each((_, a) => {
//         const href = $(a).attr('href') || '';
//         const match = href.match(/Page\$(\d+)/);
//         if (match) {
//           paginationTargets.push([parseInt(match[1]), `Page${match[1]}`]);
//         }
//       });
//     });

//     return paginationTargets;
//   }
// }

// // Usage
// async function main() {
//   const results = await new Session().scrapeWebsite();
//   console.log(`Found ${results.length} results in script.`);
//   if (results) {
//     results.forEach(result => console.log(result));
//   } else {
//     console.log('No results found or an error occurred.');
//   }
// }

// main();
