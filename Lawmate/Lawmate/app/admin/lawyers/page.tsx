"use client"

import { useState, useEffect } from "react"
import { Sidebar } from "@/components/sidebar"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { CheckCircle2, XCircle, Clock, Loader2, AlertCircle } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { getLawyers, verifyLawyer, createLawyer, uploadLawyerImage, updateLawyer, deleteLawyer, type Lawyer, type CreateLawyerRequest } from "@/lib/services/admin-lawyers"
import { resolveLawyerImageUrl } from "@/lib/services/citizen-lawyers"

export default function LawyersPage() {
  const [lawyers, setLawyers] = useState<Lawyer[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [isAddLawyerOpen, setIsAddLawyerOpen] = useState(false)
  const [isCreating, setIsCreating] = useState(false)
  const [newLawyer, setNewLawyer] = useState<CreateLawyerRequest>({
    name: "",
    email: "",
    specialization: "General Practice",
    password: "",
    location: "",
    phone: "",
    yearsExp: 0,
    bio: "",
    specializations: []
  })
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [isEditLawyerOpen, setIsEditLawyerOpen] = useState(false)
  const [editingLawyer, setEditingLawyer] = useState<Lawyer | null>(null)
  const [isUpdating, setIsUpdating] = useState(false)

  useEffect(() => {
    loadLawyers()
  }, [])

  const loadLawyers = async () => {
    try {
      setLoading(true)
      setError(null)
      const response = await getLawyers()
      setLawyers(response.lawyers)
    } catch (err: any) {
      console.error("Error loading lawyers:", err)
      setError(err.message || "Failed to load lawyers")
    } finally {
      setLoading(false)
    }
  }

  const handleVerify = async (lawyerId: string, status: "Verified" | "Rejected") => {
    try {
      await verifyLawyer(lawyerId, status)
      await loadLawyers() // Reload list
    } catch (err: any) {
      console.error("Error verifying lawyer:", err)
      alert(err.message || "Failed to verify lawyer")
    }
  }

  const handleAddLawyer = async () => {
    if (
      !newLawyer.name ||
      !newLawyer.email ||
      !newLawyer.password ||
      !newLawyer.specialization ||
      !newLawyer.location ||
      !newLawyer.phone ||
      !newLawyer.yearsExp ||
      !newLawyer.bio
    ) {
      alert("Please fill in all required lawyer details (name, email, specialization, location, phone, experience, bio, password).")
      return
    }
    setIsCreating(true)
    try {
      const created: any = await createLawyer(newLawyer)
      const newLawyerId = created?.lawyer?.id
      if (newLawyerId && imageFile) {
        await uploadLawyerImage(newLawyerId, imageFile)
      }
      setIsAddLawyerOpen(false)
      setNewLawyer({
        name: "",
        email: "",
        specialization: "General Practice",
        password: "",
        location: "",
        phone: "",
        yearsExp: 0,
        bio: "",
        specializations: []
      })
      setImageFile(null)
      await loadLawyers()
      alert("Lawyer created successfully!")
    } catch (err: any) {
      console.error("Error creating lawyer:", err)
      alert(err.message || "Failed to create lawyer")
    } finally {
      setIsCreating(false)
    }
  }

  const openEditLawyer = (lawyer: Lawyer) => {
    setEditingLawyer({ ...lawyer })
    setIsEditLawyerOpen(true)
  }

  const handleUpdateLawyer = async () => {
    if (!editingLawyer) return
    setIsUpdating(true)
    try {
      await updateLawyer(editingLawyer.id, {
        name: editingLawyer.name,
        email: editingLawyer.email,
        specialization: editingLawyer.specialization,
        location: editingLawyer.location,
        phone: editingLawyer.phone,
        yearsExp: editingLawyer.yearsExp,
        bio: editingLawyer.bio,
        casesSolved: editingLawyer.casesSolved,
        winRate: typeof editingLawyer.winRate === "number" ? editingLawyer.winRate : Number(editingLawyer.winRate) || 0,
        rating: editingLawyer.rating || 0,
        reviews: editingLawyer.reviews || 0,
        verificationStatus: editingLawyer.verificationStatus,
      })
      setIsEditLawyerOpen(false)
      setEditingLawyer(null)
      await loadLawyers()
      alert("Lawyer updated successfully!")
    } catch (err: any) {
      alert(err.message || "Failed to update lawyer")
    } finally {
      setIsUpdating(false)
    }
  }

  const handleDeleteLawyer = async (lawyerId: string, lawyerName: string) => {
    if (!confirm(`Delete lawyer "${lawyerName}"? This action cannot be undone.`)) return
    try {
      await deleteLawyer(lawyerId)
      await loadLawyers()
      alert("Lawyer deleted successfully!")
    } catch (err: any) {
      alert(err.message || "Failed to delete lawyer")
    }
  }

  const getVerificationIcon = (status: string) => {
    switch (status) {
      case "Verified":
        return <CheckCircle2 className="w-5 h-5 text-primary" />
      case "Pending":
        return <Clock className="w-5 h-5 text-accent" />
      case "Rejected":
        return <XCircle className="w-5 h-5 text-destructive" />
      default:
        return null
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Verified":
        return "bg-primary/10 text-primary"
      case "Pending":
        return "bg-accent/10 text-accent"
      case "Rejected":
        return "bg-destructive/10 text-destructive"
      default:
        return "bg-muted/10 text-muted-foreground"
    }
  }

  return (
    <div className="flex">
      <Sidebar userType="admin" />

      <main className="ml-64 w-[calc(100%-256px)] min-h-screen bg-background">
        <div className="p-8">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-foreground">Lawyer Management</h1>
              <p className="text-muted-foreground mt-2">Verify and manage lawyer profiles</p>
            </div>
            <Button onClick={() => setIsAddLawyerOpen(true)}>Add Lawyer</Button>
          </div>

          {/* Error Message */}
          {error && (
            <Card className="p-6 mb-6 border border-destructive/50 bg-destructive/10">
              <div className="flex items-center gap-3 text-destructive">
                <AlertCircle className="w-5 h-5" />
                <div>
                  <p className="font-semibold">Error loading lawyers</p>
                  <p className="text-sm">{error}</p>
                  <Button size="sm" variant="outline" className="mt-3" onClick={loadLawyers}>
                    Retry
                  </Button>
                </div>
              </div>
            </Card>
          )}

          {/* Lawyer Cards */}
          {loading ? (
            <div className="flex items-center justify-center p-12">
              <Loader2 className="w-8 h-8 animate-spin text-primary" />
              <span className="ml-3 text-muted-foreground">Loading lawyers...</span>
            </div>
          ) : (
            <div className="space-y-4">
              {lawyers.length === 0 ? (
                <Card className="p-12 text-center border border-border">
                  <p className="text-muted-foreground">No lawyers found</p>
                </Card>
              ) : (
                lawyers.map((lawyer, idx) => (
                  <Card key={`${lawyer.id}-${lawyer.email}-${idx}`} className="p-6 border border-border">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-2">
                          {lawyer.profileImage && (
                            // eslint-disable-next-line @next/next/no-img-element
                            <img src={resolveLawyerImageUrl(lawyer.profileImage)} alt={`${lawyer.name} avatar`} className="w-10 h-10 rounded-full object-cover border border-border" />
                          )}
                          {getVerificationIcon(lawyer.verificationStatus)}
                          <h3 className="text-lg font-semibold text-foreground">{lawyer.name}</h3>
                          <Badge className={getStatusColor(lawyer.verificationStatus)}>{lawyer.verificationStatus}</Badge>
                        </div>
                        <p className="text-sm text-muted-foreground mb-4">{lawyer.email}</p>

                        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                          <div>
                            <p className="text-muted-foreground">Specialization</p>
                            <p className="font-medium text-foreground">{lawyer.specialization}</p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Cases Solved</p>
                            <p className="font-medium text-foreground">{lawyer.casesSolved}</p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Win Rate</p>
                            <p className="font-medium text-foreground">
                              {typeof lawyer.winRate === "number" ? `${lawyer.winRate}%` : lawyer.winRate || "-"}
                            </p>
                          </div>
                          <div>
                            <p className="text-muted-foreground">Joined</p>
                            <p className="font-medium text-foreground">{lawyer.joinDate}</p>
                          </div>
                        </div>
                      </div>

                      <div className="flex gap-2">
                        {lawyer.verificationStatus === "Pending" && (
                          <>
                            <Button 
                              size="sm" 
                              className="bg-primary"
                              onClick={() => handleVerify(lawyer.id, "Verified")}
                            >
                              Approve
                            </Button>
                            <Button 
                              size="sm" 
                              variant="outline" 
                              className="bg-transparent"
                              onClick={() => handleVerify(lawyer.id, "Rejected")}
                            >
                              Reject
                            </Button>
                          </>
                        )}
                        {lawyer.verificationStatus === "Verified" && (
                          <>
                            <Button size="sm" variant="outline" className="bg-transparent" onClick={() => openEditLawyer(lawyer)}>
                              Edit
                            </Button>
                            <Button size="sm" variant="outline" className="bg-transparent text-destructive" onClick={() => handleDeleteLawyer(lawyer.id, lawyer.name)}>
                              Delete
                            </Button>
                          </>
                        )}
                        {lawyer.verificationStatus !== "Verified" && (
                          <>
                            <Button size="sm" variant="outline" className="bg-transparent" onClick={() => openEditLawyer(lawyer)}>
                              Edit
                            </Button>
                            <Button size="sm" variant="outline" className="bg-transparent text-destructive" onClick={() => handleDeleteLawyer(lawyer.id, lawyer.name)}>
                              Delete
                            </Button>
                          </>
                        )}
                      </div>
                    </div>
                  </Card>
                ))
              )}
            </div>
          )}

          {/* Add Lawyer Dialog */}
          <Dialog open={isAddLawyerOpen} onOpenChange={setIsAddLawyerOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Add New Lawyer</DialogTitle>
                <DialogDescription>
                  Create a new lawyer account. The lawyer will need to be verified before they can use the platform.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div>
                  <Label htmlFor="lawyer-name">Full Name</Label>
                  <Input
                    id="lawyer-name"
                    placeholder="Enter lawyer name (e.g., Adv. Sharma)"
                    value={newLawyer.name}
                    onChange={(e) => setNewLawyer({ ...newLawyer, name: e.target.value })}
                    className="mt-2"
                  />
                </div>
                <div>
                  <Label htmlFor="lawyer-email">Email</Label>
                  <Input
                    id="lawyer-email"
                    type="email"
                    placeholder="lawyer@example.com"
                    value={newLawyer.email}
                    onChange={(e) => setNewLawyer({ ...newLawyer, email: e.target.value })}
                    className="mt-2"
                  />
                </div>
                <div>
                  <Label htmlFor="specialization">Specialization</Label>
                  <Input
                    id="specialization"
                    placeholder="e.g., Criminal Law, Bail & Remand"
                    value={newLawyer.specialization}
                    onChange={(e) => setNewLawyer({ ...newLawyer, specialization: e.target.value })}
                    className="mt-2"
                  />
                </div>
                <div>
                  <Label htmlFor="location">Location</Label>
                  <Input
                    id="location"
                    placeholder="e.g., Lahore"
                    value={newLawyer.location}
                    onChange={(e) => setNewLawyer({ ...newLawyer, location: e.target.value })}
                    className="mt-2"
                  />
                </div>
                <div>
                  <Label htmlFor="phone">Phone</Label>
                  <Input
                    id="phone"
                    placeholder="+92-3xx-xxxxxxx"
                    value={newLawyer.phone}
                    onChange={(e) => setNewLawyer({ ...newLawyer, phone: e.target.value })}
                    className="mt-2"
                  />
                </div>
                <div>
                  <Label htmlFor="years-exp">Years of Experience</Label>
                  <Input
                    id="years-exp"
                    type="number"
                    min={0}
                    value={newLawyer.yearsExp}
                    onChange={(e) => setNewLawyer({ ...newLawyer, yearsExp: Number(e.target.value) || 0 })}
                    className="mt-2"
                  />
                </div>
                <div>
                  <Label htmlFor="multi-specializations">Specializations (comma separated)</Label>
                  <Input
                    id="multi-specializations"
                    placeholder="Bail, Appeals, Evidence"
                    onChange={(e) =>
                      setNewLawyer({
                        ...newLawyer,
                        specializations: e.target.value
                          .split(",")
                          .map((s) => s.trim())
                          .filter(Boolean),
                      })
                    }
                    className="mt-2"
                  />
                </div>
                <div>
                  <Label htmlFor="bio">Bio</Label>
                  <Input
                    id="bio"
                    placeholder="Short lawyer profile bio"
                    value={newLawyer.bio}
                    onChange={(e) => setNewLawyer({ ...newLawyer, bio: e.target.value })}
                    className="mt-2"
                  />
                </div>
                <div>
                  <Label htmlFor="lawyer-image">Profile Image</Label>
                  <Input
                    id="lawyer-image"
                    type="file"
                    accept="image/png,image/jpeg,image/jpg,image/webp"
                    onChange={(e) => setImageFile(e.target.files?.[0] || null)}
                    className="mt-2"
                  />
                </div>
                <div>
                  <Label htmlFor="lawyer-password">Password</Label>
                  <Input
                    id="lawyer-password"
                    type="password"
                    placeholder="Enter password"
                    value={newLawyer.password}
                    onChange={(e) => setNewLawyer({ ...newLawyer, password: e.target.value })}
                    className="mt-2"
                  />
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsAddLawyerOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleAddLawyer} disabled={isCreating}>
                  {isCreating ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    "Create Lawyer"
                  )}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>

          {/* Edit Lawyer Dialog */}
          <Dialog open={isEditLawyerOpen} onOpenChange={setIsEditLawyerOpen}>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Edit Lawyer</DialogTitle>
                <DialogDescription>Update lawyer professional profile details.</DialogDescription>
              </DialogHeader>
              {editingLawyer && (
                <div className="space-y-4 py-4">
                  <div>
                    <Label>Name</Label>
                    <Input className="mt-2" value={editingLawyer.name} onChange={(e) => setEditingLawyer({ ...editingLawyer, name: e.target.value })} />
                  </div>
                  <div>
                    <Label>Email</Label>
                    <Input className="mt-2" value={editingLawyer.email} onChange={(e) => setEditingLawyer({ ...editingLawyer, email: e.target.value })} />
                  </div>
                  <div>
                    <Label>Specialization</Label>
                    <Input className="mt-2" value={editingLawyer.specialization} onChange={(e) => setEditingLawyer({ ...editingLawyer, specialization: e.target.value })} />
                  </div>
                  <div>
                    <Label>Location</Label>
                    <Input className="mt-2" value={editingLawyer.location || ""} onChange={(e) => setEditingLawyer({ ...editingLawyer, location: e.target.value })} />
                  </div>
                  <div>
                    <Label>Phone</Label>
                    <Input className="mt-2" value={editingLawyer.phone || ""} onChange={(e) => setEditingLawyer({ ...editingLawyer, phone: e.target.value })} />
                  </div>
                  <div>
                    <Label>Experience (years)</Label>
                    <Input className="mt-2" type="number" min={0} value={editingLawyer.yearsExp || 0} onChange={(e) => setEditingLawyer({ ...editingLawyer, yearsExp: Number(e.target.value) || 0 })} />
                  </div>
                  <div>
                    <Label>Bio</Label>
                    <Input className="mt-2" value={editingLawyer.bio || ""} onChange={(e) => setEditingLawyer({ ...editingLawyer, bio: e.target.value })} />
                  </div>
                  <div>
                    <Label>Cases Solved</Label>
                    <Input
                      className="mt-2"
                      type="number"
                      min={0}
                      value={editingLawyer.casesSolved || 0}
                      onChange={(e) => setEditingLawyer({ ...editingLawyer, casesSolved: Number(e.target.value) || 0 })}
                    />
                  </div>
                  <div>
                    <Label>Win Rate (%)</Label>
                    <Input
                      className="mt-2"
                      type="number"
                      min={0}
                      max={100}
                      value={typeof editingLawyer.winRate === "number" ? editingLawyer.winRate : Number(editingLawyer.winRate) || 0}
                      onChange={(e) => setEditingLawyer({ ...editingLawyer, winRate: Number(e.target.value) || 0 })}
                    />
                  </div>
                  <div>
                    <Label>Rating (0-5)</Label>
                    <Input
                      className="mt-2"
                      type="number"
                      min={0}
                      max={5}
                      step="0.1"
                      value={editingLawyer.rating || 0}
                      onChange={(e) => setEditingLawyer({ ...editingLawyer, rating: Number(e.target.value) || 0 })}
                    />
                  </div>
                  <div>
                    <Label>Reviews Count</Label>
                    <Input
                      className="mt-2"
                      type="number"
                      min={0}
                      value={editingLawyer.reviews || 0}
                      onChange={(e) => setEditingLawyer({ ...editingLawyer, reviews: Number(e.target.value) || 0 })}
                    />
                  </div>
                  <div>
                    <Label>Verification Status</Label>
                    <Select
                      value={editingLawyer.verificationStatus}
                      onValueChange={(value) =>
                        setEditingLawyer({
                          ...editingLawyer,
                          verificationStatus: value as "Verified" | "Pending" | "Rejected",
                        })
                      }
                    >
                      <SelectTrigger className="mt-2">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        <SelectItem value="Pending">Pending</SelectItem>
                        <SelectItem value="Verified">Verified</SelectItem>
                        <SelectItem value="Rejected">Rejected</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              )}
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsEditLawyerOpen(false)}>Cancel</Button>
                <Button onClick={handleUpdateLawyer} disabled={isUpdating}>
                  {isUpdating ? "Updating..." : "Save Changes"}
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </main>
    </div>
  )
}
