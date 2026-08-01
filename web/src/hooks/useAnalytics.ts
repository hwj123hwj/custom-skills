/**
 * Analytics Hook — 百度统计 + Google Analytics (GA4)
 *
 * Why: 本站是 HashRouter SPA，百度统计默认只在首次加载时记一次 PV。
 *      GA4 的 gtag 有内置 history 监听，对 hash 路由的子页面覆盖也不完整。
 *      此 hook 在路由切换时手动上报 PV，保证每个技能/agent 页面都被正确统计。
 *
 * 上报逻辑：
 * - 百度统计：调用 _hmt.push(['_trackPageview', pagePath])
 * - GA4：调用 gtag('event', 'page_view', { page_location, page_title })
 */

import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'

// 声明全局变量，避免 TS 报错
declare global {
  interface Window {
    _hmt?: Array<[string, ...unknown[]]>
    gtag?: (...args: unknown[]) => void
  }
}

/**
 * 路由变化时触发双统计 PV 上报。
 * 放在 Router 内层使用（见 App.tsx）。
 */
export function useAnalytics() {
  const location = useLocation()

  useEffect(() => {
    // hash router 的真实路径在 location.hash 里（如 #/skill/xxx）
    // 没有 hash 时（首次加载根路径）默认为 '/'
    const pagePath = location.hash ? location.hash.replace('#', '') : location.pathname || '/'
    const pageUrl = `${window.location.origin}/${pagePath.replace(/^\//, '')}`

    // 1. 百度统计 SPA PV 上报
    if (typeof window._hmt !== 'undefined') {
      window._hmt.push(['_trackPageview', pagePath])
    }

    // 2. GA4 PV 上报（GA4 支持 event page_view）
    if (typeof window.gtag !== 'undefined') {
      window.gtag('event', 'page_view', {
        page_location: pageUrl,
        page_path: pagePath,
        page_title: document.title,
      })
    }
  }, [location])
}
