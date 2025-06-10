package com.example.mdmjive.receivers

import android.app.admin.DeviceAdminReceiver
import android.app.admin.DevicePolicyManager
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.os.Build
import android.util.Log

class MDMDeviceAdminReceiver : DeviceAdminReceiver() {

    override fun onEnabled(context: Context, intent: Intent) {
        super.onEnabled(context, intent)
        Log.d("MDM", "Admin enabled")
        setupDeviceAdmin(context)
    }

    // Configura el dispositivo con las políticas de administración
    private fun setupDeviceAdmin(context: Context) {
        val dpm = context.getSystemService(Context.DEVICE_POLICY_SERVICE) as DevicePolicyManager
        val componentName = ComponentName(context, MDMDeviceAdminReceiver::class.java)

        // Verifica si la app es propietaria del dispositivo
        if (dpm.isDeviceOwnerApp(context.packageName)) {
            Log.d("MDM", "La app es propietaria del dispositivo. Aplicando políticas.")
            applyPolicies(dpm, componentName)
            startMDMService(context)
        } else {
            Log.e("MDM", "La app no es propietaria del dispositivo.")
        }
    }

    // Aplica las políticas de seguridad en el dispositivo
    private fun applyPolicies(dpm: DevicePolicyManager, componentName: ComponentName) {
        try {
            // Aplicando las políticas
            dpm.apply {
                setLockTaskPackages(componentName, arrayOf(packageName))
                setCameraDisabled(componentName, true)
                setKeyguardDisabled(componentName, true)

                // Políticas adicionales de seguridad
                setPasswordQuality(componentName, DevicePolicyManager.PASSWORD_QUALITY_COMPLEX)
                setMaximumFailedPasswordsForWipe(componentName, 10)
                setMaximumTimeToLock(componentName, 30000L) // 30 segundos de bloqueo
            }
            Log.d("MDM", "Políticas aplicadas correctamente.")
        } catch (e: Exception) {
            Log.e("MDM", "Error aplicando políticas: ${e.message}")
        }
    }

    // Inicia el servicio MDM
    private fun startMDMService(context: Context) {
        try {
            // Verifica si el sistema soporta el servicio de fondo
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                context.startForegroundService(Intent(context, com.example.mdmjive.services.MDMService::class.java))
            } else {
                context.startService(Intent(context, com.example.mdmjive.services.MDMService::class.java))
            }
            Log.d("MDM", "Servicio MDM iniciado.")
        } catch (e: Exception) {
            Log.e("MDM", "Error iniciando el servicio MDM: ${e.message}")
        }
    }

    // Este método se llama cuando el dispositivo pierde la administración
    override fun onDisabled(context: Context, intent: Intent) {
        super.onDisabled(context, intent)
        Log.d("MDM", "Admin disabled - Intentando reactivar.")
        reactivateAdmin(context)
    }

    // Reactiva los permisos de administrador si es necesario
    private fun reactivateAdmin(context: Context) {
        val intent = Intent(DevicePolicyManager.ACTION_ADD_DEVICE_ADMIN).apply {
            putExtra(DevicePolicyManager.EXTRA_DEVICE_ADMIN,
                ComponentName(context, MDMDeviceAdminReceiver::class.java))
            putExtra(DevicePolicyManager.EXTRA_ADD_EXPLANATION,
                "Los permisos de administrador son necesarios para el funcionamiento del sistema")
            flags = Intent.FLAG_ACTIVITY_NEW_TASK
        }
        context.startActivity(intent)
    }
}
