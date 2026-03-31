package com.eos.eapps.core.common

import com.eos.eapps.core.common.utils.MathUtils
import com.eos.eapps.core.common.utils.StringUtils

/**
 * eApps Core Common — foundation library shared by all apps.
 *
 * Provides: data models (AppInfo, ThemeConfig, UserPrefs),
 * utilities (MathUtils, StringUtils, DateUtils, ExpressionParser),
 * and the AppRegistry listing all 38 apps.
 */
object EAppsCommon {

    const val VERSION = "0.1.0"
    const val APP_NAME = "eApps"
    const val PACKAGE_NAME = "com.eos.eapps"
    const val TOTAL_APPS = 38
    fun searchApps(query: String): List<AppInfo> = AppRegistry.search(query)
}
