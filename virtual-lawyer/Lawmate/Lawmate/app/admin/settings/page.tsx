"use client"

import { Sidebar } from "@/components/sidebar"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Switch } from "@/components/ui/switch"
import { Label } from "@/components/ui/label"
import { Input } from "@/components/ui/input"
import { useState, useEffect } from "react"
import { getAdminSettings, updateAdminSettings, type AdminSettings } from "@/lib/services/admin"
import { Loader2, AlertCircle, CheckCircle2 } from "lucide-react"

export default function AdminSettingsPage() {
  const [settings, setSettings] = useState<AdminSettings>({
    platform_name: "Lawmate",
    support_email: "support@justiceai.com",
    max_file_upload_size_mb: 50,
    email_notifications: true,
    ai_monitoring: true,
    auto_backup: true,
    maintenance_mode: false,
  })
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getAdminSettings()
      setSettings(data)
    } catch (err: any) {
      console.error("Error loading settings:", err)
      setError(err.message || "Failed to load settings")
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    setSaving(true)
    setError(null)
    setSuccess(false)
    try {
      await updateAdminSettings(settings)
      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
    } catch (err: any) {
      console.error("Error saving settings:", err)
      setError(err.message || "Failed to save settings")
    } finally {
      setSaving(false)
    }
  }

  const handleReset = async () => {
    if (confirm("Are you sure you want to reset all settings to defaults?")) {
      const defaultSettings: AdminSettings = {
        platform_name: "Lawmate",
        support_email: "support@justiceai.com",
        max_file_upload_size_mb: 50,
        email_notifications: true,
        ai_monitoring: true,
        auto_backup: true,
        maintenance_mode: false,
      }
      setSettings(defaultSettings)
      await updateAdminSettings(defaultSettings)
    }
  }

  return (
    <div className="flex">
      <Sidebar userType="admin" />

      <main className="ml-64 w-[calc(100%-256px)] min-h-screen bg-background">
        <div className="p-8">
          {/* Header */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-foreground">System Settings</h1>
            <p className="text-muted-foreground mt-2">Configure platform-wide settings and preferences</p>
          </div>

          {/* Error/Success Messages */}
          {error && (
            <Card className="p-4 mb-6 border border-destructive/50 bg-destructive/10">
              <div className="flex items-center gap-3 text-destructive">
                <AlertCircle className="w-5 h-5" />
                <p>{error}</p>
              </div>
            </Card>
          )}
          {success && (
            <Card className="p-4 mb-6 border border-green-500/50 bg-green-500/10">
              <div className="flex items-center gap-3 text-green-600">
                <CheckCircle2 className="w-5 h-5" />
                <p>Settings saved successfully!</p>
              </div>
            </Card>
          )}

          {loading ? (
            <div className="flex items-center justify-center p-12">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
              <span className="ml-3 text-muted-foreground">Loading settings...</span>
            </div>
          ) : (
            <>
              {/* General Settings */}
              <Card className="p-6 border border-border mb-6">
                <h2 className="text-lg font-semibold text-foreground mb-4">General Settings</h2>
                <div className="space-y-4">
                  <div>
                    <Label htmlFor="platform-name">Platform Name</Label>
                    <Input
                      id="platform-name"
                      value={settings.platform_name}
                      onChange={(e) => setSettings({ ...settings, platform_name: e.target.value })}
                      className="mt-1 border-2 border-border focus:border-primary"
                    />
                  </div>
                  <div>
                    <Label htmlFor="support-email">Support Email</Label>
                    <Input
                      id="support-email"
                      type="email"
                      value={settings.support_email}
                      onChange={(e) => setSettings({ ...settings, support_email: e.target.value })}
                      className="mt-1 border-2 border-border focus:border-primary"
                    />
                  </div>
                  <div>
                    <Label htmlFor="max-file-size">Max File Upload Size (MB)</Label>
                    <Input
                      id="max-file-size"
                      type="number"
                      value={settings.max_file_upload_size_mb}
                      onChange={(e) => setSettings({ ...settings, max_file_upload_size_mb: parseInt(e.target.value) || 50 })}
                      className="mt-1 border-2 border-border focus:border-primary"
                    />
                  </div>
                </div>
              </Card>

              {/* Feature Toggles */}
              <Card className="p-6 border border-border mb-6">
                <h2 className="text-lg font-semibold text-foreground mb-4">Feature Toggles</h2>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <Label>Email Notifications</Label>
                    <Switch
                      checked={settings.email_notifications}
                      onCheckedChange={(checked) => setSettings({ ...settings, email_notifications: checked })}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label>AI Response Monitoring</Label>
                    <Switch
                      checked={settings.ai_monitoring}
                      onCheckedChange={(checked) => setSettings({ ...settings, ai_monitoring: checked })}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label>Automatic Database Backups</Label>
                    <Switch
                      checked={settings.auto_backup}
                      onCheckedChange={(checked) => setSettings({ ...settings, auto_backup: checked })}
                    />
                  </div>
                  <div className="flex items-center justify-between">
                    <Label>Maintenance Mode</Label>
                    <Switch
                      checked={settings.maintenance_mode}
                      onCheckedChange={(checked) => setSettings({ ...settings, maintenance_mode: checked })}
                    />
                  </div>
                </div>
              </Card>

              {/* Actions */}
              <div className="flex gap-3">
                <Button onClick={handleSave} disabled={saving}>
                  {saving ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Saving...
                    </>
                  ) : (
                    "Save Settings"
                  )}
                </Button>
                <Button variant="outline" onClick={handleReset} disabled={saving}>
                  Reset to Defaults
                </Button>
              </div>
            </>
          )}
        </div>
      </main>
    </div>
  )
}
