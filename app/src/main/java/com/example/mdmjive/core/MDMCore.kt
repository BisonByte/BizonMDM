package com.example.mdmjive.core

import android.content.Context
import com.example.mdmjive.security.PolicyManager
import com.example.mdmjive.security.SecurityChecker
import com.example.mdmjive.monitor.DeviceMonitor
import com.example.mdmjive.remote.RemoteControlManager
import com.example.mdmjive.logging.LogManager

class MDMCore private constructor(private val context: Context) {
    private val policyManager: PolicyManager
    private val securityChecker: SecurityChecker
    private val deviceMonitor: DeviceMonitor
    private val remoteControl: RemoteControlManager
    private val logManager: LogManager

    init {
        // Inicialización segura de componentes
        policyManager = PolicyManager(context)
        securityChecker = SecurityChecker
        deviceMonitor = DeviceMonitor(context)
        remoteControl = RemoteControlManager(context)
        logManager = LogManager()
    }

    companion object {
        @Volatile private var instance: MDMCore? = null

        fun getInstance(context: Context): MDMCore {
            return instance ?: synchronized(this) {
                instance ?: MDMCore(context).also { instance = it }
            }
        }
    }

    // Métodos para interactuar con los componentes
    fun getPolicyManager(): PolicyManager {
        return policyManager
    }

    fun getSecurityChecker(): SecurityChecker {
        return securityChecker
    }

    fun getDeviceMonitor(): DeviceMonitor {
        return deviceMonitor
    }

    fun getRemoteControlManager(): RemoteControlManager {
        return remoteControl
    }

    fun getLogManager(): LogManager {
        return logManager
    }
}
