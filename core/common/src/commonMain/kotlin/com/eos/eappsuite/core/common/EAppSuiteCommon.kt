package com.eos.eappsuite.core.common

object EAppSuiteCommon {
    const val VERSION = "1.0.0"
    const val APP_NAME = "eAppSuite"
    const val PACKAGE_NAME = "com.eos.eappsuite"
    const val TOTAL_APPS = 38
}
package com.eos.eappsuite.core.common

import com.eos.eappsuite.core.common.constants.AppRegistry
import com.eos.eappsuite.core.common.models.AppCategory
import com.eos.eappsuite.core.common.models.AppInfo
import com.eos.eappsuite.core.common.models.Platform
import com.eos.eappsuite.core.common.models.ThemeConfig
import com.eos.eappsuite.core.common.models.UserPrefs
import com.eos.eappsuite.core.common.utils.DateUtils
import com.eos.eappsuite.core.common.utils.ExpressionParser
import com.eos.eappsuite.core.common.utils.MathUtils
import com.eos.eappsuite.core.common.utils.StringUtils

/**
 * eAppSuite Core Common — foundation library shared by all apps.
 *
 * Provides: data models (AppInfo, ThemeConfig, UserPrefs),
 * utilities (MathUtils, StringUtils, DateUtils, ExpressionParser),
 * and the AppRegistry listing all 38 apps.
 */
object EAppSuiteCommon {
    const val VERSION = "1.0.0"
    const val APP_COUNT = 38

    val allApps: List<AppInfo> get() = AppRegistry.apps
    val categories: List<AppCategory> get() = AppCategory.entries

    fun getApp(id: String): AppInfo? = AppRegistry.getApp(id)
    fun searchApps(query: String): List<AppInfo> = AppRegistry.search(query)
}
