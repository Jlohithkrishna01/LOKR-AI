/**
 * Utilities for extracting and formatting user preferred names
 * for LOKR AI professional greetings.
 */

const TITLES_REGEX = /^(dr\.?|mr\.?|mrs\.?|ms\.?|prof\.?|er\.?|shri\.?|smt\.?)\s+/i;

const COMPOUND_SUFFIXES = [
  'krishna',
  'kumar',
  'prasad',
  'reddy',
  'rao',
  'sharma',
  'singh',
  'babu',
  'teja',
  'vardhan',
  'nathan',
  'murthy',
];

const GENERIC_NAMES = new Set([
  'guest',
  'guest explorer',
  'user',
  'anonymous',
  'none',
  'null',
  'test',
  'tester',
  'benchmark tester',
  'unknown',
  'admin',
  'developer',
  'there',
]);

/**
 * Extracts a natural, preferred first name from a user's full name.
 * 
 * Examples:
 * - 'J Lohithkrishna' -> 'Lohith'
 * - 'J. Lohithkrishna' -> 'Lohith'
 * - 'Jangiti Lohithkrishna' -> 'Lohith'
 * - 'Lohithkrishna' -> 'Lohith'
 * - 'John Doe' -> 'John'
 * - 'Alice Smith' -> 'Alice'
 * - 'Dr. Jane Watson' -> 'Jane'
 * - 'Guest Explorer' -> null
 */
export function extractPreferredName(fullName?: string | null): string | null {
  if (!fullName) return null;

  let name = fullName.trim();
  if (!name || name.length < 2) return null;

  if (GENERIC_NAMES.has(name.toLowerCase())) {
    return null;
  }

  // 1. Remove titles/honorifics
  name = name.replace(TITLES_REGEX, '').trim();

  const tokens = name.split(/\s+/).filter(Boolean);
  if (tokens.length === 0) return null;

  // 2. Filter out single-letter initials (with or without dot)
  const nonInitialTokens = tokens.filter((t) => {
    const clean = t.replace(/\.$/, '');
    return clean.length > 1 && !(clean.length === 2 && clean === clean.toUpperCase());
  });

  let candidate = nonInitialTokens.length > 0 ? nonInitialTokens[0] : tokens[0].replace(/\.$/, '');

  // 3. Handle known surnames if placed first, e.g. 'Jangiti Lohithkrishna'
  if (candidate.toLowerCase() === 'jangiti' && nonInitialTokens.length > 1) {
    candidate = nonInitialTokens[1];
  }

  // 4. Handle compound Indian names: e.g. 'Lohithkrishna' -> 'Lohith'
  const candidateLower = candidate.toLowerCase();
  for (const suffix of COMPOUND_SUFFIXES) {
    if (candidateLower.endsWith(suffix) && candidateLower.length > suffix.length + 2) {
      candidate = candidate.slice(0, -suffix.length);
      break;
    }
  }

  candidate = candidate.trim();
  if (!candidate || GENERIC_NAMES.has(candidate.toLowerCase())) {
    return null;
  }

  return candidate.charAt(0).toUpperCase() + candidate.slice(1).toLowerCase();
}
