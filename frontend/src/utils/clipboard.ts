/**
 * Universal clipboard copy utility supporting:
 * - Desktop browsers (modern Clipboard API)
 * - Mobile devices (iOS Safari, Android Chrome)
 * - Insecure contexts (HTTP over LAN IP e.g. http://192.168.x.x or http://10.x.x.x)
 */
export async function copyToClipboard(text: string): Promise<boolean> {
  if (!text) return false;

  // 1. Try modern navigator.clipboard if available in a secure context (https / localhost)
  if (typeof navigator !== 'undefined' && navigator.clipboard && window.isSecureContext) {
    try {
      await navigator.clipboard.writeText(text);
      return true;
    } catch (err) {
      console.warn('navigator.clipboard.writeText failed, falling back to execCommand:', err);
    }
  }

  // 2. Mobile & Insecure HTTP Fallback using textarea + execCommand
  try {
    const textArea = document.createElement('textarea');
    textArea.value = text;

    // Prevent zoom and layout shift on mobile screens
    textArea.style.fontSize = '16px';
    textArea.style.position = 'fixed';
    textArea.style.top = '0';
    textArea.style.left = '0';
    textArea.style.width = '2em';
    textArea.style.height = '2em';
    textArea.style.padding = '0';
    textArea.style.border = 'none';
    textArea.style.outline = 'none';
    textArea.style.boxShadow = 'none';
    textArea.style.background = 'transparent';
    textArea.style.opacity = '0';
    textArea.style.zIndex = '-9999';
    textArea.setAttribute('readonly', ''); // Prevent keyboard on mobile

    document.body.appendChild(textArea);

    // iOS Safari selection workaround
    if (typeof navigator !== 'undefined' && /ipad|ipod|iphone/i.test(navigator.userAgent)) {
      textArea.contentEditable = 'true';
      textArea.readOnly = false;
      const range = document.createRange();
      range.selectNodeContents(textArea);
      const selection = window.getSelection();
      if (selection) {
        selection.removeAllRanges();
        selection.addRange(range);
      }
      textArea.setSelectionRange(0, 999999);
    } else {
      textArea.select();
    }

    const successful = document.execCommand('copy');
    document.body.removeChild(textArea);
    return successful;
  } catch (err) {
    console.error('All clipboard copy methods failed:', err);
    return false;
  }
}
