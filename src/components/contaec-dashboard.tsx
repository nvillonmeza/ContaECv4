'use client';

import Image from 'next/image';
import { useState, useEffect, useCallback } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert';
import {
  BookOpen,
  Building2,
  ChevronLeft,
  ChevronRight,
  FileText,
  LayoutDashboard,
  Key,
  LogOut,
  Menu,
  Moon,
  Plus,
  RefreshCw,
  Settings,
  Shield,
  ShieldAlert,
  Sun,
  User,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock,
  Database,
  DollarSign,
  Receipt,
  Server,
  TrendingUp,
  Users,
  Briefcase,
  X,
  Loader2,
  Trash2,
  Pencil,
  Wrench,
  Package,
  Truck,
  ShoppingCart,
  ScrollText,
  Globe,
  Warehouse as WarehouseIcon,
  Monitor,
  PieChart,
  Kanban,
  Plug,
  Brain,
  Activity,
} from 'lucide-react';
import { useTheme } from 'next-themes';
import { toast } from 'sonner';
import { getCurrentLocale, setCurrentLocale, getLocaleLabel, LOCALES, type Locale } from '@/lib/i18n';
import { ContaECSettings } from '@/components/contaec-settings';
import { ContaECInvoices } from '@/components/contaec-invoices';
import { ContaECInventory } from '@/components/contaec-inventory';
import { ContaECHR } from '@/components/contaec-hr';
import { ContaECSuppliers } from '@/components/contaec-suppliers';
import { ContaECPurchases } from '@/components/contaec-purchases';
import { ContaECAudit } from '@/components/contaec-audit';
import { ContaECWarehouses } from '@/components/contaec-warehouses';
import { ContaECPOS } from '@/components/contaec-pos';
import { ContaECBudgets } from '@/components/contaec-budgets';
import { ContaECCRM } from '@/components/contaec-crm';
import { ContaECProjects } from '@/components/contaec-projects';
import { ContaECIntegrations } from '@/components/contaec-integrations';
import { ContaECMLAI } from '@/components/contaec-ml-ai';
import { ContaECAccounting } from '@/components/contaec-accounting';
import {
  logout,
  clearTokens,
  getLicenseStatus,
  getLicenseOptions,
  getCompanies,
  createCompany,
  updateCompany,
  deleteCompany,
  lookupRuc,
  getSRIIVARates,
  getSRIDocumentTypes,
  getSRITipoIdentificacion,
  getInvoiceStats,
  type User as UserType,
  type LicenseStatus as LicenseStatusType,
  type LicenseOptions as LicenseOptionsType,
  type Company as CompanyType,
  type SRIIVARate,
  type SRIDocumentType,
  type SRICatalog,
  type InvoiceStats as InvoiceStatsType,
} from '@/lib/api';

interface ContaECDashboardProps {
  user: UserType;
  onLogout: () => void;
}

type NavItem = 'dashboard' | 'companies' | 'sri' | 'license' | 'invoices' | 'proformas' | 'products' | 'inventory' | 'warehouses' | 'pos' | 'hr' | 'suppliers' | 'purchases' | 'budgets' | 'crm' | 'projects' | 'integrations' | 'mlai' | 'accounting' | 'audit' | 'settings' | 'admin-overview' | 'admin-users' | 'admin-system' | 'admin-licenses' | 'admin-security';

export function ContaECDashboard({ user, onLogout }: ContaECDashboardProps) {
  const { theme, setTheme } = useTheme();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeNav, setActiveNav] = useState<NavItem>('dashboard');
  const [license, setLicense] = useState<LicenseStatusType | null>(null);
  const [companies, setCompanies] = useState<CompanyType[]>([]);
  const selectedCompanyId = companies.length > 0 ? companies[0].id : undefined;
  const [invoiceStats, setInvoiceStats] = useState<InvoiceStatsType | null>(null);
  const [ivaRates, setIvaRates] = useState<SRIIVARate[]>([]);
  const [documentTypes, setDocumentTypes] = useState<SRIDocumentType[]>([]);
  const [identTypes, setIdentTypes] = useState<SRICatalog[]>([]);
  const [loading, setLoading] = useState(true);
  const [licenseExpiring, setLicenseExpiring] = useState(false);
  const [locale, setLocale] = useState<Locale>(getCurrentLocale);

  // New company dialog
  const [showNewCompany, setShowNewCompany] = useState(false);
  const [newCompany, setNewCompany] = useState({
    ruc: '',
    razon_social: '',
    nombre_comercial: '',
    dir_matriz: '',
    cod_establecimiento: '001',
    cod_punto_emision: '001',
    obligado_contabilidad: '',
    contribuyente_especial: '',
  });
  const [creatingCompany, setCreatingCompany] = useState(false);

  const loadDashboardData = useCallback(async () => {
    setLoading(true);
    try {
      const results = await Promise.allSettled([
        getLicenseStatus(),
        getCompanies(),
        getSRIIVARates(),
        getSRIDocumentTypes(),
        getSRITipoIdentificacion(),
        getInvoiceStats(),
      ]);

      // Detect session expiry: if ALL API calls are rejected, session is invalid
      const allRejected = results.every(r => r.status === 'rejected');
      if (allRejected) {
        clearTokens();
        onLogout();
        toast.error('Sesion expirada. Por favor inicie sesion nuevamente.');
        return;
      }

      if (results[0].status === 'fulfilled') {
        const lic = results[0].value;
        setLicense(lic);
        // Check if license expires within 30 days
        if (lic.days_remaining !== null) {
          setLicenseExpiring(lic.days_remaining <= 30 && lic.days_remaining > 0);
        }
      }
      if (results[1].status === 'fulfilled' && Array.isArray(results[1].value)) setCompanies(results[1].value);
      if (results[2].status === 'fulfilled' && Array.isArray(results[2].value)) setIvaRates(results[2].value);
      if (results[3].status === 'fulfilled' && Array.isArray(results[3].value)) setDocumentTypes(results[3].value);
      if (results[4].status === 'fulfilled' && Array.isArray(results[4].value)) setIdentTypes(results[4].value);
      if (results[5].status === 'fulfilled') setInvoiceStats(results[5].value);
    } catch {
      toast.error('Error al cargar datos del panel');
    } finally {
      setLoading(false);
    }
  }, [onLogout]);

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);

  async function handleCreateCompany() {
    setCreatingCompany(true);
    try {
      const company = await createCompany(newCompany);
      setCompanies((prev) => [...prev, company]);
      setShowNewCompany(false);
      setNewCompany({
        ruc: '',
        razon_social: '',
        nombre_comercial: '',
        dir_matriz: '',
        cod_establecimiento: '001',
        cod_punto_emision: '001',
        obligado_contabilidad: '',
        contribuyente_especial: '',
      });
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Error al crear empresa');
    } finally {
      setCreatingCompany(false);
    }
  }

  function handleLogout() {
    logout();
    onLogout();
  }

  const userNavItems: { id: NavItem; label: string; icon: React.ReactNode }[] = [
    { id: 'dashboard', label: 'Panel Principal', icon: <LayoutDashboard className="h-4 w-4" /> },
    { id: 'companies', label: 'Empresas', icon: <Building2 className="h-4 w-4" /> },
    { id: 'sri', label: 'Catalogos SRI', icon: <Shield className="h-4 w-4" /> },
    { id: 'license', label: 'Licencia', icon: <FileText className="h-4 w-4" /> },
    { id: 'invoices', label: 'Comprobantes', icon: <Receipt className="h-4 w-4" /> },
    { id: 'proformas', label: 'Proformas', icon: <FileText className="h-4 w-4" /> },
    { id: 'products', label: 'Productos', icon: <Package className="h-4 w-4" /> },
    { id: 'inventory', label: 'Inventario', icon: <Database className="h-4 w-4" /> },
    { id: 'warehouses', label: 'Almacenes', icon: <WarehouseIcon className="h-4 w-4" /> },
    { id: 'pos', label: 'Punto de Venta', icon: <Monitor className="h-4 w-4" /> },
    { id: 'hr', label: 'Recursos Humanos', icon: <Users className="h-4 w-4" /> },
    { id: 'suppliers', label: 'Proveedores', icon: <Truck className="h-4 w-4" /> },
    { id: 'purchases', label: 'Compras', icon: <ShoppingCart className="h-4 w-4" /> },
    { id: 'budgets', label: 'Presupuestos', icon: <PieChart className="h-4 w-4" /> },
    { id: 'crm', label: 'CRM', icon: <Kanban className="h-4 w-4" /> },
    { id: 'projects', label: 'Proyectos', icon: <Briefcase className="h-4 w-4" /> },
    { id: 'integrations', label: 'Integraciones', icon: <Plug className="h-4 w-4" /> },
    { id: 'mlai', label: 'ML / IA', icon: <Brain className="h-4 w-4" /> },
    { id: 'accounting', label: 'Contabilidad', icon: <BookOpen className="h-4 w-4" /> },
    { id: 'audit', label: 'Auditoria', icon: <ScrollText className="h-4 w-4" /> },
    { id: 'settings', label: 'Configuracion', icon: <Wrench className="h-4 w-4" /> },
  ];

  const adminNavItems: { id: NavItem; label: string; icon: React.ReactNode }[] = [
    { id: 'admin-overview', label: 'Resumen', icon: <Activity className="h-4 w-4" /> },
    { id: 'admin-users', label: 'Usuarios', icon: <Users className="h-4 w-4" /> },
    { id: 'admin-system', label: 'Sistema', icon: <Server className="h-4 w-4" /> },
    { id: 'admin-licenses', label: 'Licencias', icon: <Key className="h-4 w-4" /> },
    { id: 'admin-security', label: 'Seguridad', icon: <ShieldAlert className="h-4 w-4" /> },
  ];

  // Admin users see admin tabs, regular users see normal nav items
  const navItems = user.is_admin ? adminNavItems : userNavItems;

  return (
    <div className="min-h-screen flex bg-background">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? 'w-64' : 'w-16'
        } border-r bg-card transition-all duration-300 flex flex-col shrink-0`}
      >
        {/* Sidebar Header */}
        <div className="p-4 border-b flex items-center gap-3">
          <div className="rounded-lg bg-primary/10 p-1.5 shrink-0">
            <Image
              src="/logo.svg"
              alt="ContaEC"
              width={32}
              height={32}
              className="h-8 w-8"
              priority
            />
          </div>
          {sidebarOpen && (
            <div className="overflow-hidden">
              <h2 className="font-bold text-sm leading-tight">ContaEC</h2>
              <p className="text-[10px] text-muted-foreground truncate">Facturacion Electronica</p>
            </div>
          )}
        </div>

        {/* Nav Items */}
        <nav className="flex-1 p-2 space-y-1">
          {navItems.map((item) => (
            <button
              key={item.id}
              onClick={() => setActiveNav(item.id)}
              className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm transition-colors ${
                activeNav === item.id
                  ? 'bg-primary/10 text-primary font-medium'
                  : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
              }`}
            >
              {item.icon}
              {sidebarOpen && <span>{item.label}</span>}
            </button>
          ))}
        </nav>

        {/* Sidebar Footer */}
        <div className="p-2 border-t">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="w-full flex items-center justify-center gap-2 px-3 py-2 rounded-lg text-sm text-muted-foreground hover:bg-accent hover:text-accent-foreground transition-colors"
          >
            {sidebarOpen ? (
              <>
                <ChevronLeft className="h-4 w-4" />
                <span>Colapsar</span>
              </>
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top Bar */}
        <header className="h-14 border-b bg-card flex items-center justify-between px-4 shrink-0">
          <div className="flex items-center gap-2">
            <Button
              variant="ghost"
              size="icon"
              className="sm:hidden"
              onClick={() => setSidebarOpen(!sidebarOpen)}
            >
              <Menu className="h-5 w-5" />
            </Button>
            <h1 className="text-lg font-semibold hidden sm:block">
              {navItems.find((n) => n.id === activeNav)?.label || 'Panel Principal'}
            </h1>
          </div>

          <div className="flex items-center gap-2">
            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" size="icon" title="Idioma">
                  <Globe className="h-4 w-4" />
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                {LOCALES.map((l) => (
                  <DropdownMenuItem
                    key={l}
                    className={locale === l ? 'bg-accent' : ''}
                    onClick={() => { setLocale(l); setCurrentLocale(l); }}
                  >
                    {getLocaleLabel(l)}
                  </DropdownMenuItem>
                ))}
              </DropdownMenuContent>
            </DropdownMenu>

            <Button
              variant="ghost"
              size="icon"
              onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            >
              {theme === 'dark' ? (
                <Sun className="h-4 w-4" />
              ) : (
                <Moon className="h-4 w-4" />
              )}
            </Button>

            <DropdownMenu>
              <DropdownMenuTrigger asChild>
                <Button variant="ghost" className="gap-2">
                  <div className="h-7 w-7 rounded-full bg-primary/10 flex items-center justify-center">
                    <User className="h-4 w-4 text-primary" />
                  </div>
                  <span className="text-sm hidden sm:inline">{user.full_name}</span>
                </Button>
              </DropdownMenuTrigger>
              <DropdownMenuContent align="end">
                <DropdownMenuItem disabled>
                  <User className="mr-2 h-4 w-4" />
                  {user.email}
                </DropdownMenuItem>
                <DropdownMenuSeparator />
                <DropdownMenuItem onClick={handleLogout} className="text-destructive">
                  <LogOut className="mr-2 h-4 w-4" />
                  Cerrar Sesion
                </DropdownMenuItem>
              </DropdownMenuContent>
            </DropdownMenu>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6">
          {loading ? (
            <div className="flex items-center justify-center h-64">
              <Loader2 className="h-8 w-8 animate-spin text-primary" />
            </div>
          ) : user.is_admin ? (
            <AdminDashboardView onLogout={onLogout} />
          ) : (
            <>
              {activeNav === 'dashboard' && (
                <DashboardView
                  user={user}
                  license={license}
                  licenseExpiring={licenseExpiring}
                  companies={companies}
                  invoiceStats={invoiceStats}
                  ivaRates={ivaRates}
                  documentTypes={documentTypes}
                />
              )}
              {activeNav === 'companies' && (
                <CompaniesView
                  companies={companies}
                  onNewCompany={() => setShowNewCompany(true)}
                  onCompaniesChanged={loadDashboardData}
                />
              )}
              {activeNav === 'sri' && (
                <SRIView
                  ivaRates={ivaRates}
                  documentTypes={documentTypes}
                  identTypes={identTypes}
                />
              )}
              {activeNav === 'license' && (
                <LicenseView license={license} licenseExpiring={licenseExpiring} />
              )}
              {activeNav === 'invoices' && (
                <ContaECInvoices user={user} companies={companies} />
              )}
              {activeNav === 'proformas' && (
                <ContaECInvoices user={user} companies={companies} initialTab="proformas" />
              )}
              {activeNav === 'products' && (
                <ContaECInvoices user={user} companies={companies} initialTab="productos" />
              )}
              {activeNav === 'inventory' && (
                <ContaECInventory user={user} companies={companies} />
              )}
              {activeNav === 'warehouses' && (
                <ContaECWarehouses user={user} companies={companies} />
              )}
              {activeNav === 'pos' && (
                <ContaECPOS user={user} companies={companies} />
              )}
              {activeNav === 'hr' && (
                <ContaECHR user={user} companies={companies} />
              )}
              {activeNav === 'suppliers' && (
                <ContaECSuppliers user={user} companies={companies} />
              )}
              {activeNav === 'purchases' && (
                <ContaECPurchases user={user} companies={companies} />
              )}
              {activeNav === 'budgets' && (
                <ContaECBudgets user={user} companies={companies} />
              )}
              {activeNav === 'crm' && (
                <ContaECCRM user={user} companies={companies} />
              )}
              {activeNav === 'projects' && (
                <ContaECProjects user={user} companies={companies} />
              )}
              {activeNav === 'integrations' && (
                <ContaECIntegrations user={user} companies={companies} />
              )}
              {activeNav === 'mlai' && (
                <ContaECMLAI user={user} companies={companies} />
              )}
              {activeNav === 'accounting' && selectedCompanyId && (
                <ContaECAccounting companyId={selectedCompanyId} />
              )}
              {activeNav === 'audit' && (
                <ContaECAudit />
              )}
              {activeNav === 'settings' && (
                <ContaECSettings user={user} />
              )}
            </>
          )}
        </main>

        {/* Sticky Footer */}
        <footer className="border-t bg-card py-3 px-4 text-center shrink-0">
          <p className="text-xs text-muted-foreground">
            Desarrollado por <span className="font-semibold text-foreground">T&amp;M Technology Ec</span>
            &nbsp;&mdash;&nbsp; info@tymtechnology.shop &nbsp;|&nbsp; 0960068866
          </p>
        </footer>
      </div>

      {/* New Company Dialog */}
      <Dialog open={showNewCompany} onOpenChange={setShowNewCompany}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Nueva Empresa</DialogTitle>
            <DialogDescription>
              Registre una nueva empresa para emitir comprobantes electronicos
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="nc-ruc">RUC</Label>
                <div className="flex gap-2">
                  <Input
                    id="nc-ruc"
                    placeholder="1790000000001"
                    value={newCompany.ruc}
                    onChange={(e) => setNewCompany({ ...newCompany, ruc: e.target.value })}
                    maxLength={13}
                  />
                  <Button
                    type="button"
                    variant="outline"
                    size="sm"
                    disabled={newCompany.ruc.length !== 13 || !/^\d+$/.test(newCompany.ruc)}
                    onClick={async () => {
                      if (newCompany.ruc.length !== 13) return;
                      try {
                        const data = await lookupRuc(newCompany.ruc);
                        if (data.razon_social) {
                          setNewCompany((prev) => ({
                            ...prev,
                            razon_social: data.razon_social || prev.razon_social,
                            nombre_comercial: data.nombre_comercial || prev.nombre_comercial,
                            dir_matriz: data.dir_matriz || prev.dir_matriz,
                            obligado_contabilidad: data.obligado_contabilidad || prev.obligado_contabilidad,
                            contribuyente_especial: data.contribuyente_especial || prev.contribuyente_especial,
                          }));
                          toast.success('Datos cargados desde el SRI');
                        } else if (data.message) {
                          toast.warning(data.message);
                        }
                      } catch {
                        toast.error('Error consultando RUC al SRI');
                      }
                    }}
                  >
                    Buscar en SRI
                  </Button>
                </div>
              </div>
              <div className="space-y-2">
                <Label htmlFor="nc-cod-est">Cod. Establecimiento</Label>
                <Input
                  id="nc-cod-est"
                  placeholder="001"
                  value={newCompany.cod_establecimiento}
                  onChange={(e) => setNewCompany({ ...newCompany, cod_establecimiento: e.target.value })}
                  maxLength={3}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="nc-razon">Razon Social</Label>
              <Input
                id="nc-razon"
                placeholder="Mi Empresa S.A."
                value={newCompany.razon_social}
                onChange={(e) => setNewCompany({ ...newCompany, razon_social: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="nc-nombre">Nombre Comercial</Label>
              <Input
                id="nc-nombre"
                placeholder="Mi Empresa"
                value={newCompany.nombre_comercial}
                onChange={(e) => setNewCompany({ ...newCompany, nombre_comercial: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="nc-dir">Direccion Matriz</Label>
              <Input
                id="nc-dir"
                placeholder="Av. Amazonas 123, Quito"
                value={newCompany.dir_matriz}
                onChange={(e) => setNewCompany({ ...newCompany, dir_matriz: e.target.value })}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="nc-cod-pemi">Cod. Punto Emision</Label>
                <Input
                  id="nc-cod-pemi"
                  placeholder="001"
                  value={newCompany.cod_punto_emision}
                  onChange={(e) => setNewCompany({ ...newCompany, cod_punto_emision: e.target.value })}
                  maxLength={3}
                />
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setShowNewCompany(false)}>
                Cancelar
              </Button>
              <Button onClick={handleCreateCompany} disabled={creatingCompany}>
                {creatingCompany ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Creando...
                  </>
                ) : (
                  'Crear Empresa'
                )}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

// --- Sub-views ---

function DashboardView({
  user,
  license,
  licenseExpiring,
  companies,
  invoiceStats,
  ivaRates,
  documentTypes,
}: {
  user: UserType;
  license: LicenseStatusType | null;
  licenseExpiring: boolean;
  companies: CompanyType[];
  invoiceStats: InvoiceStatsType | null;
  ivaRates: SRIIVARate[];
  documentTypes: SRIDocumentType[];
}) {
  return (
    <div className="space-y-6">
      {/* License Alert */}
      {licenseExpiring && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Licencia por expirar</AlertTitle>
          <AlertDescription>
            Su licencia esta por expirar. Renueve para continuar emitiendo comprobantes electronicos.
          </AlertDescription>
        </Alert>
      )}

      {/* Welcome */}
      <div>
        <h2 className="text-2xl font-bold">
          Bienvenido, {user.full_name || user.email}
        </h2>
        <p className="text-muted-foreground">
          Panel de control de ContaEC - Contabilidad y Facturacion Electronica
        </p>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <QuickStatCard
          title="Empresas"
          value={companies.length}
          icon={<Building2 className="h-4 w-4" />}
          description="registradas"
        />
        <QuickStatCard
          title="Comprobantes"
          value={invoiceStats?.total ?? 0}
          icon={<Receipt className="h-4 w-4" />}
          description="emitidos"
        />
        <QuickStatCard
          title="Aprobados SRI"
          value={invoiceStats?.autorizado ?? 0}
          icon={<CheckCircle2 className="h-4 w-4" />}
          description="este mes"
        />
        <QuickStatCard
          title="Rechazados"
          value={invoiceStats?.rechazado ?? 0}
          icon={<XCircle className="h-4 w-4" />}
          description="este mes"
          variant="warning"
        />
      </div>

      {/* License Status + SRI Catalogs Preview */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* License Card */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <FileText className="h-4 w-4 text-primary" />
              Estado de Licencia
            </CardTitle>
          </CardHeader>
          <CardContent>
            {license ? (
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Tipo</span>
                  <Badge variant="secondary" className="capitalize">
                    {license.license_type || 'Sin licencia'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Estado</span>
                  <Badge
                    variant={license.is_active ? 'default' : 'destructive'}
                    className={license.is_active ? 'bg-primary' : ''}
                  >
                    {license.is_active ? 'Activa' : 'Inactiva'}
                  </Badge>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm text-muted-foreground">Expiracion</span>
                  <span className="text-sm font-medium">
                    {license.license_end_date
                      ? new Date(license.license_end_date).toLocaleDateString('es-EC')
                      : 'Sin limite'}
                  </span>
                </div>
                {license.days_remaining !== null && (
                  <>
                    <Separator />
                    <div className="flex items-center justify-between">
                      <span className="text-sm text-muted-foreground">Dias Restantes</span>
                      <span
                        className={`text-sm font-medium ${
                          license.days_remaining <= 0
                            ? 'text-destructive'
                            : license.days_remaining <= 30
                            ? 'text-amber-500'
                            : 'text-emerald-600'
                        }`}
                      >
                        {license.days_remaining} dias
                      </span>
                    </div>
                  </>
                )}
              </div>
            ) : (
              <div className="text-center py-4">
                <AlertTriangle className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
                <p className="text-sm text-muted-foreground">
                  No se pudo cargar la informacion de licencia
                </p>
              </div>
            )}
          </CardContent>
        </Card>

        {/* SRI Catalogs Preview */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base flex items-center gap-2">
              <Shield className="h-4 w-4 text-primary" />
              Catalogos SRI
            </CardTitle>
            <CardDescription>
              Tasas de IVA y tipos de documento vigentes
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div>
                <h4 className="text-sm font-medium mb-2">Tasas de IVA</h4>
                {ivaRates.length > 0 ? (
                  <div className="grid grid-cols-2 gap-2">
                    {ivaRates.slice(0, 6).map((rate) => (
                      <div
                        key={rate.codigo}
                        className="flex items-center justify-between rounded-md border px-3 py-1.5"
                      >
                        <span className="text-xs">{rate.descripcion}</span>
                        <Badge variant="secondary" className="text-xs">
                          {rate.porcentaje}%
                        </Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-muted-foreground">
                    No se pudieron cargar las tasas de IVA
                  </p>
                )}
              </div>
              <Separator />
              <div>
                <h4 className="text-sm font-medium mb-2">Tipos de Documento</h4>
                {documentTypes.length > 0 ? (
                  <div className="space-y-1">
                    {documentTypes.slice(0, 5).map((dt) => (
                      <div
                        key={dt.codigo}
                        className="flex items-center justify-between rounded-md border px-3 py-1.5"
                      >
                        <span className="text-xs">{dt.descripcion}</span>
                        <Badge variant="outline" className="text-xs">
                          {dt.codigo}
                        </Badge>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-xs text-muted-foreground">
                    No se pudieron cargar los tipos de documento
                  </p>
                )}
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Companies Quick List */}
      <Card>
        <CardHeader className="pb-3">
          <CardTitle className="text-base flex items-center gap-2">
            <Building2 className="h-4 w-4 text-primary" />
            Empresas Registradas
          </CardTitle>
        </CardHeader>
        <CardContent>
          {companies.length > 0 ? (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {companies.map((company) => (
                <div
                  key={company.id}
                  className="rounded-lg border p-4 hover:bg-accent/50 transition-colors"
                >
                  <div className="flex items-start justify-between">
                    <div>
                      <h4 className="text-sm font-medium">{company.razon_social}</h4>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        RUC: {company.ruc}
                      </p>
                    </div>
                    <Badge
                      variant={company.is_active ? 'default' : 'secondary'}
                      className={company.is_active ? 'bg-primary' : ''}
                    >
                      {company.is_active ? 'Activa' : 'Inactiva'}
                    </Badge>
                  </div>
                  {company.nombre_comercial && (
                    <p className="text-xs text-muted-foreground mt-2">
                      {company.nombre_comercial}
                    </p>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Building2 className="h-8 w-8 mx-auto text-muted-foreground mb-2" />
              <p className="text-sm text-muted-foreground">
                No hay empresas registradas. Agregue una para comenzar.
              </p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

function QuickStatCard({
  title,
  value,
  icon,
  description,
  variant = 'default',
}: {
  title: string;
  value: number;
  icon: React.ReactNode;
  description: string;
  variant?: 'default' | 'warning';
}) {
  return (
    <Card>
      <CardContent className="p-4">
        <div className="flex items-center justify-between mb-2">
          <span className="text-xs text-muted-foreground">{title}</span>
          <div
            className={`rounded-md p-1.5 ${
              variant === 'warning' ? 'bg-destructive/10' : 'bg-primary/10'
            }`}
          >
            <span className={variant === 'warning' ? 'text-destructive' : 'text-primary'}>
              {icon}
            </span>
          </div>
        </div>
        <div className="text-2xl font-bold">{value}</div>
        <p className="text-xs text-muted-foreground">{description}</p>
      </CardContent>
    </Card>
  );
}

function CompaniesView({
  companies,
  onNewCompany,
  onCompaniesChanged,
}: {
  companies: CompanyType[];
  onNewCompany: () => void;
  onCompaniesChanged: () => void;
}) {
  const [editingCompany, setEditingCompany] = useState<CompanyType | null>(null);
  const [deletingCompanyId, setDeletingCompanyId] = useState<string | null>(null);
  const [operating, setOperating] = useState(false);
  const [editForm, setEditForm] = useState({
    ruc: '',
    razon_social: '',
    nombre_comercial: '',
    dir_matriz: '',
    cod_establecimiento: '',
    cod_punto_emision: '',
  });

  function handleEditClick(company: CompanyType) {
    setEditingCompany(company);
    setEditForm({
      ruc: company.ruc,
      razon_social: company.razon_social,
      nombre_comercial: company.nombre_comercial || '',
      dir_matriz: company.dir_matriz,
      cod_establecimiento: company.cod_establecimiento,
      cod_punto_emision: company.cod_punto_emision,
    });
  }

  async function handleEditSave() {
    if (!editingCompany) return;
    setOperating(true);
    try {
      await updateCompany(editingCompany.id, editForm);
      setEditingCompany(null);
      onCompaniesChanged();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Error al guardar cambios');
    } finally {
      setOperating(false);
    }
  }

  async function handleDeleteConfirm() {
    if (!deletingCompanyId) return;
    setOperating(true);
    try {
      await deleteCompany(deletingCompanyId);
      setDeletingCompanyId(null);
      onCompaniesChanged();
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Error al eliminar empresa');
    } finally {
      setOperating(false);
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Empresas</h2>
          <p className="text-muted-foreground">
            Gestione las empresas registradas en el sistema
          </p>
        </div>
        <Button onClick={onNewCompany}>
          <Plus className="mr-2 h-4 w-4" />
          Nueva Empresa
        </Button>
      </div>

      {companies.length > 0 ? (
        <Card>
          <CardContent className="p-0">
            <ScrollArea className="max-h-96">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>RUC</TableHead>
                    <TableHead>Razon Social</TableHead>
                    <TableHead>Nombre Comercial</TableHead>
                    <TableHead>Estado</TableHead>
                    <TableHead className="text-right">Acciones</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {companies.map((company) => (
                    <TableRow key={company.id}>
                      <TableCell className="font-mono text-xs">{company.ruc}</TableCell>
                      <TableCell className="font-medium">{company.razon_social}</TableCell>
                      <TableCell className="text-muted-foreground">
                        {company.nombre_comercial || '-'}
                      </TableCell>
                      <TableCell>
                        <Badge
                          variant={company.is_active ? 'default' : 'secondary'}
                          className={company.is_active ? 'bg-primary' : ''}
                        >
                          {company.is_active ? 'Activa' : 'Inactiva'}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-1">
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8"
                            onClick={() => handleEditClick(company)}
                          >
                            <Pencil className="h-3.5 w-3.5" />
                          </Button>
                          <Button
                            variant="ghost"
                            size="icon"
                            className="h-8 w-8 text-destructive"
                            onClick={() => setDeletingCompanyId(company.id)}
                          >
                            <Trash2 className="h-3.5 w-3.5" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </ScrollArea>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardContent className="py-12 text-center">
            <Building2 className="h-12 w-12 mx-auto text-muted-foreground mb-3" />
            <h3 className="text-lg font-medium">Sin empresas</h3>
            <p className="text-muted-foreground text-sm mt-1">
              Registre una empresa para comenzar a emitir comprobantes
            </p>
            <Button className="mt-4" onClick={onNewCompany}>
              <Plus className="mr-2 h-4 w-4" />
              Registrar Empresa
            </Button>
          </CardContent>
        </Card>
      )}

      {/* Edit Company Dialog */}
      <Dialog open={!!editingCompany} onOpenChange={(open) => { if (!open) setEditingCompany(null); }}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>Editar Empresa</DialogTitle>
            <DialogDescription>
              Modifique los datos de la empresa
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="edit-ruc">RUC</Label>
                <Input
                  id="edit-ruc"
                  value={editForm.ruc}
                  onChange={(e) => setEditForm({ ...editForm, ruc: e.target.value })}
                  maxLength={13}
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="edit-cod-est">Cod. Establecimiento</Label>
                <Input
                  id="edit-cod-est"
                  value={editForm.cod_establecimiento}
                  onChange={(e) => setEditForm({ ...editForm, cod_establecimiento: e.target.value })}
                  maxLength={3}
                />
              </div>
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-razon">Razon Social</Label>
              <Input
                id="edit-razon"
                value={editForm.razon_social}
                onChange={(e) => setEditForm({ ...editForm, razon_social: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-nombre">Nombre Comercial</Label>
              <Input
                id="edit-nombre"
                value={editForm.nombre_comercial}
                onChange={(e) => setEditForm({ ...editForm, nombre_comercial: e.target.value })}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="edit-dir">Direccion Matriz</Label>
              <Input
                id="edit-dir"
                value={editForm.dir_matriz}
                onChange={(e) => setEditForm({ ...editForm, dir_matriz: e.target.value })}
              />
            </div>
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="edit-cod-pemi">Cod. Punto Emision</Label>
                <Input
                  id="edit-cod-pemi"
                  value={editForm.cod_punto_emision}
                  onChange={(e) => setEditForm({ ...editForm, cod_punto_emision: e.target.value })}
                  maxLength={3}
                />
              </div>
            </div>
            <div className="flex justify-end gap-2">
              <Button variant="outline" onClick={() => setEditingCompany(null)}>
                Cancelar
              </Button>
              <Button onClick={handleEditSave} disabled={operating}>
                {operating ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Guardando...
                  </>
                ) : (
                  'Guardar Cambios'
                )}
              </Button>
            </div>
          </div>
        </DialogContent>
      </Dialog>

      {/* Delete Company Confirmation Dialog */}
      <Dialog open={!!deletingCompanyId} onOpenChange={(open) => { if (!open) setDeletingCompanyId(null); }}>
        <DialogContent className="sm:max-w-sm">
          <DialogHeader>
            <DialogTitle>Eliminar Empresa</DialogTitle>
            <DialogDescription>
              Esta seguro de que desea eliminar esta empresa? Esta accion no se puede deshacer.
            </DialogDescription>
          </DialogHeader>
          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => setDeletingCompanyId(null)}>
              Cancelar
            </Button>
            <Button variant="destructive" onClick={handleDeleteConfirm} disabled={operating}>
              {operating ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  Eliminando...
                </>
              ) : (
                'Eliminar'
              )}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function SRIView({
  ivaRates,
  documentTypes,
  identTypes,
}: {
  ivaRates: SRIIVARate[];
  documentTypes: SRIDocumentType[];
  identTypes: SRICatalog[];
}) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Catalogos SRI</h2>
        <p className="text-muted-foreground">
          Catalogos del Servicio de Rentas Internas del Ecuador
        </p>
      </div>

      <Tabs defaultValue="iva" className="space-y-4">
        <TabsList>
          <TabsTrigger value="iva">Tasas IVA</TabsTrigger>
          <TabsTrigger value="docs">Tipos de Documento</TabsTrigger>
          <TabsTrigger value="ident">Tipos de Identificacion</TabsTrigger>
        </TabsList>

        <TabsContent value="iva">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Tasas de IVA</CardTitle>
              <CardDescription>Impuesto al Valor Agregado vigente en Ecuador</CardDescription>
            </CardHeader>
            <CardContent>
              {ivaRates.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Codigo</TableHead>
                      <TableHead>Descripcion</TableHead>
                      <TableHead className="text-right">Porcentaje</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {ivaRates.map((rate) => (
                      <TableRow key={rate.codigo}>
                        <TableCell className="font-mono text-xs">{rate.codigo}</TableCell>
                        <TableCell>{rate.descripcion}</TableCell>
                        <TableCell className="text-right font-medium">{rate.porcentaje}%</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <p className="text-sm text-muted-foreground text-center py-6">
                  No se pudieron cargar las tasas de IVA. Verifique la conexion con el servidor.
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="docs">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Tipos de Documento Electronico</CardTitle>
              <CardDescription>Comprobantes electronicos reconocidos por el SRI</CardDescription>
            </CardHeader>
            <CardContent>
              {documentTypes.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Codigo</TableHead>
                      <TableHead>Descripcion</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {documentTypes.map((dt) => (
                      <TableRow key={dt.codigo}>
                        <TableCell className="font-mono text-xs">{dt.codigo}</TableCell>
                        <TableCell>{dt.descripcion}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <p className="text-sm text-muted-foreground text-center py-6">
                  No se pudieron cargar los tipos de documento.
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="ident">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Tipos de Identificacion</CardTitle>
              <CardDescription>Tipos de identificacion para contribuyentes</CardDescription>
            </CardHeader>
            <CardContent>
              {identTypes.length > 0 ? (
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Codigo</TableHead>
                      <TableHead>Descripcion</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {identTypes.map((it) => (
                      <TableRow key={it.codigo}>
                        <TableCell className="font-mono text-xs">{it.codigo}</TableCell>
                        <TableCell>{it.descripcion}</TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              ) : (
                <p className="text-sm text-muted-foreground text-center py-6">
                  No se pudieron cargar los tipos de identificacion.
                </p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}

function LicenseView({
  license,
  licenseExpiring,
}: {
  license: LicenseStatusType | null;
  licenseExpiring: boolean;
}) {
  const [licenseOptions, setLicenseOptions] = useState<LicenseOptionsType | null>(null);
  const [loadingOptions, setLoadingOptions] = useState(false);

  useEffect(() => {
    if (!license) {
      setLoadingOptions(true);
      getLicenseOptions()
        .then((data) => {
          if (data && Array.isArray(data.options)) setLicenseOptions(data);
        })
        .catch(() => toast.error('Error al cargar opciones de licencia'))
        .finally(() => setLoadingOptions(false));
    }
  }, [license]);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Licencia</h2>
        <p className="text-muted-foreground">
          Informacion de su licencia ContaEC
        </p>
      </div>

      {licenseExpiring && license && (
        <Alert variant="destructive">
          <AlertTriangle className="h-4 w-4" />
          <AlertTitle>Licencia por expirar</AlertTitle>
          <AlertDescription>
            Su licencia esta proxima a expirar. Contacte a T&amp;M Technology Ec para renovar.
          </AlertDescription>
        </Alert>
      )}

      {license ? (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Detalles de Licencia</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Tipo</span>
                <Badge className="capitalize bg-primary">{license.license_type || 'Sin licencia'}</Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Estado</span>
                <Badge variant={license.is_active ? 'default' : 'destructive'}>
                  {license.is_active ? 'Activa' : 'Inactiva'}
                </Badge>
              </div>
              <Separator />
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Fecha de Expiracion</span>
                <span className="text-sm font-medium">
                  {license.license_end_date
                    ? new Date(license.license_end_date).toLocaleDateString('es-EC', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                      })
                    : 'Sin limite'}
                </span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Fecha de Activacion</span>
                <span className="text-sm font-medium">
                  {license.license_start_date
                    ? new Date(license.license_start_date).toLocaleDateString('es-EC', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric',
                      })
                    : 'No disponible'}
                </span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Estado de Licencia</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Expirada</span>
                <Badge variant={license.is_expired ? 'destructive' : 'default'}>
                  {license.is_expired ? 'Si' : 'No'}
                </Badge>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Dias Restantes</span>
                <span className={`text-sm font-medium ${
                  license.days_remaining === null
                    ? ''
                    : license.days_remaining <= 0
                    ? 'text-destructive'
                    : license.days_remaining <= 30
                    ? 'text-amber-500'
                    : 'text-emerald-600'
                }`}>
                  {license.days_remaining !== null ? `${license.days_remaining} dias` : 'Sin limite'}
                </span>
              </div>
              <Separator />
              <div className="flex justify-between items-center">
                <span className="text-sm text-muted-foreground">Activa</span>
                <CheckCircle2 className={`h-5 w-5 ${license.is_active ? 'text-emerald-600' : 'text-muted-foreground'}`} />
              </div>
            </CardContent>
          </Card>
        </div>
      ) : (
        <div className="space-y-6">
          <Card>
            <CardContent className="py-12 text-center">
              <AlertTriangle className="h-12 w-12 mx-auto text-amber-500 mb-3" />
              <h3 className="text-lg font-medium">Sin licencia activa</h3>
              <p className="text-muted-foreground text-sm mt-1">
                No se encontro informacion de licencia. Seleccione un plan a continuacion o contacte al administrador.
              </p>
            </CardContent>
          </Card>

          {/* License Options */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Planes Disponibles</h3>
            {loadingOptions ? (
              <div className="flex justify-center py-8">
                <Loader2 className="h-8 w-8 animate-spin text-primary" />
              </div>
            ) : licenseOptions ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {licenseOptions.options.map((option) => (
                  <Card key={option.type} className="hover:border-primary transition-colors">
                    <CardHeader className="pb-3">
                      <CardTitle className="text-lg">{option.label}</CardTitle>
                      <CardDescription>{option.months} {option.months === 1 ? 'mes' : 'meses'}</CardDescription>
                    </CardHeader>
                    <CardContent className="space-y-3">
                      <div className="text-center">
                        <span className="text-3xl font-bold">${option.price.toFixed(2)}</span>
                        <p className="text-xs text-muted-foreground">
                          ${(option.price / option.months).toFixed(2)}/mes
                        </p>
                      </div>
                      <Button
                        className="w-full"
                        onClick={() => {
                          const msg = `Hola, soy ${encodeURIComponent('usuario@email.com')}. Me interesa el plan ${encodeURIComponent(option.label)} de $${option.price}.`;
                          window.open(`https://wa.me/${licenseOptions.contact_whatsapp}?text=${msg}`, '_blank');
                        }}
                      >
                        Contactar por WhatsApp
                      </Button>
                    </CardContent>
                  </Card>
                ))}
              </div>
            ) : (
              <p className="text-sm text-muted-foreground text-center py-4">
                No se pudieron cargar las opciones de licencia.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

function InvoicesView({ invoiceStats }: { invoiceStats: InvoiceStatsType | null }) {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Comprobantes Electronicos</h2>
        <p className="text-muted-foreground">
          Resumen de comprobantes emitidos
        </p>
      </div>

      {invoiceStats ? (
        <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
          <Card>
            <CardContent className="p-4 text-center">
              <Receipt className="h-6 w-6 mx-auto text-primary mb-2" />
              <div className="text-2xl font-bold">{invoiceStats.total}</div>
              <p className="text-xs text-muted-foreground">Total Emitidos</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <Clock className="h-6 w-6 mx-auto text-muted-foreground mb-2" />
              <div className="text-2xl font-bold">{invoiceStats.borrador}</div>
              <p className="text-xs text-muted-foreground">Borradores</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <FileText className="h-6 w-6 mx-auto text-primary mb-2" />
              <div className="text-2xl font-bold">{invoiceStats.enviado}</div>
              <p className="text-xs text-muted-foreground">Enviados al SRI</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <CheckCircle2 className="h-6 w-6 mx-auto text-green-600 mb-2" />
              <div className="text-2xl font-bold">{invoiceStats.autorizado}</div>
              <p className="text-xs text-muted-foreground">Aprobados</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <XCircle className="h-6 w-6 mx-auto text-destructive mb-2" />
              <div className="text-2xl font-bold">{invoiceStats.rechazado}</div>
              <p className="text-xs text-muted-foreground">Rechazados</p>
            </CardContent>
          </Card>
          <Card>
            <CardContent className="p-4 text-center">
              <DollarSign className="h-6 w-6 mx-auto text-primary mb-2" />
              <div className="text-2xl font-bold">
                ${invoiceStats.total_amount.toLocaleString('es-EC', { minimumFractionDigits: 2 })}
              </div>
              <p className="text-xs text-muted-foreground">Monto Total</p>
            </CardContent>
          </Card>
        </div>
      ) : (
        <Card>
          <CardContent className="py-12 text-center">
            <Receipt className="h-12 w-12 mx-auto text-muted-foreground mb-3" />
            <h3 className="text-lg font-medium">Sin datos de comprobantes</h3>
            <p className="text-muted-foreground text-sm mt-1">
              No se pudieron cargar las estadisticas de comprobantes.
            </p>
          </CardContent>
        </Card>
      )}
    </div>
  );
}

// ─── Admin Dashboard View (integrated into main dashboard) ────────────────
function AdminDashboardView({ onLogout }: { onLogout: () => void }) {
  const [activeAdminTab, setActiveAdminTab] = useState('overview');
  const [adminStats, setAdminStats] = useState<{
    total_users: number;
    total_companies: number;
    total_clients: number;
    expiring_licenses: number;
    expired_licenses: number;
    license_distribution: Record<string, number>;
  } | null>(null);
  const [adminUsers, setAdminUsers] = useState<Array<{
    id: string;
    email: string;
    full_name: string;
    is_active: boolean;
    is_admin: boolean;
    license_type: string;
    license_end_date: string | null;
    created_at: string;
  }>>([]);
  const [health, setHealth] = useState<{
    system: Record<string, unknown>;
    database: Record<string, unknown>;
    application: Record<string, unknown>;
  } | null>(null);
  const [securityData, setSecurityData] = useState<{
    expired_active_licenses: Array<{ user_id: string; email: string; full_name: string; license_end_date: string | null; days_expired: number | null }>;
    users_without_config: Array<{ user_id: string; email: string; full_name: string }>;
  } | null>(null);
  const [loading, setLoading] = useState(true);
  const [licenseDialogOpen, setLicenseDialogOpen] = useState(false);
  const [selectedUserId, setSelectedUserId] = useState('');
  const [licenseForm, setLicenseForm] = useState({ license_type: '' });
  const [modifying, setModifying] = useState(false);
  const [licensePrices, setLicensePrices] = useState<Array<{ type: string; key: string; price: number; months: number; color: string }>>([
    { type: 'Mensual', key: 'monthly', price: 15.00, months: 1, color: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200' },
    { type: 'Trimestral', key: 'quarterly', price: 40.00, months: 3, color: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200' },
    { type: 'Semestral', key: 'semiannual', price: 75.00, months: 6, color: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200' },
    { type: 'Anual', key: 'annual', price: 130.00, months: 12, color: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200' },
  ]);
  const [editingPrice, setEditingPrice] = useState<string | null>(null);
  const [priceForm, setPriceForm] = useState<Record<string, number>>({});
  const [savingPrices, setSavingPrices] = useState(false);

  const loadAdminData = useCallback(async () => {
    setLoading(true);
    try {
      const token = localStorage.getItem('contaec_token') || '';
      const headers = { headers: { Authorization: `Bearer ${token}` } };
      const results = await Promise.allSettled([
        fetch('/api/v1/admin/dashboard', headers).then(r => r.ok ? r.json() : Promise.reject(r.status)),
        fetch('/api/v1/admin/users', headers).then(r => r.ok ? r.json() : Promise.reject(r.status)),
        fetch('/api/v1/admin/system-health', headers).then(r => r.ok ? r.json() : Promise.reject(r.status)),
        fetch('/api/v1/admin/security-issues', headers).then(r => r.ok ? r.json() : Promise.reject(r.status)),
        fetch('/api/v1/admin/license-prices', headers).then(r => r.ok ? r.json() : Promise.reject(r.status)),
      ]);

      // Detect session expiry: if ALL admin API calls are rejected, session is invalid
      const allRejected = results.every(r => r.status === 'rejected');
      if (allRejected) {
        clearTokens();
        onLogout();
        toast.error('Sesion expirada. Por favor inicie sesion nuevamente.');
        return;
      }

      if (results[0].status === 'fulfilled') setAdminStats(results[0].value);
      if (results[1].status === 'fulfilled' && Array.isArray(results[1].value)) setAdminUsers(results[1].value);
      if (results[2].status === 'fulfilled') setHealth(results[2].value);
      if (results[3].status === 'fulfilled') setSecurityData(results[3].value);
      // Load license prices from API
      if (results[4].status === 'fulfilled' && results[4].value?.prices) {
        const prices = results[4].value.prices;
        const colorMap: Record<string, string> = {
          monthly: 'bg-blue-100 text-blue-800 dark:bg-blue-900 dark:text-blue-200',
          quarterly: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
          semiannual: 'bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200',
          annual: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200',
        };
        setLicensePrices([
          { type: prices.monthly?.label || 'Mensual', key: 'monthly', price: prices.monthly?.price || 15, months: prices.monthly?.months || 1, color: colorMap.monthly },
          { type: prices.quarterly?.label || 'Trimestral', key: 'quarterly', price: prices.quarterly?.price || 40, months: prices.quarterly?.months || 3, color: colorMap.quarterly },
          { type: prices.semiannual?.label || 'Semestral', key: 'semiannual', price: prices.semiannual?.price || 75, months: prices.semiannual?.months || 6, color: colorMap.semiannual },
          { type: prices.annual?.label || 'Anual', key: 'annual', price: prices.annual?.price || 130, months: prices.annual?.months || 12, color: colorMap.annual },
        ]);
        setPriceForm({
          monthly: prices.monthly?.price || 15,
          quarterly: prices.quarterly?.price || 40,
          semiannual: prices.semiannual?.price || 75,
          annual: prices.annual?.price || 130,
        });
      }
    } catch {
      toast.error('Error al cargar datos de administracion');
    } finally {
      setLoading(false);
    }
  }, [onLogout]);

  useEffect(() => {
    loadAdminData();
  }, [loadAdminData]);

  async function handleModifyLicense() {
    if (!selectedUserId) return;
    setModifying(true);
    try {
      const token = localStorage.getItem('contaec_token') || '';
      const res = await fetch(`/api/v1/admin/users/${selectedUserId}/license?license_type=${licenseForm.license_type}`, {
        method: 'PUT',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) throw new Error('Error al modificar licencia');
      toast.success('Licencia actualizada');
      setLicenseDialogOpen(false);
      loadAdminData();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Error al modificar licencia');
    } finally {
      setModifying(false);
    }
  }

  async function handleToggleUser(userId: string, isActive: boolean) {
    try {
      const token = localStorage.getItem('contaec_token') || '';
      const res = await fetch(`/api/v1/admin/users/${userId}/active?is_active=${!isActive}`, {
        method: 'PUT',
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!res.ok) {
        const error = await res.json().catch(() => ({ detail: 'Error al cambiar estado' }));
        throw new Error(error.detail || 'Error al cambiar estado');
      }
      toast.success(isActive ? 'Usuario desactivado' : 'Usuario activado');
      loadAdminData();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Error');
    }
  }

  async function handleSavePrices() {
    setSavingPrices(true);
    try {
      const token = localStorage.getItem('contaec_token') || '';
      const res = await fetch('/api/v1/admin/license-prices', {
        method: 'PUT',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(priceForm),
      });
      if (!res.ok) throw new Error('Error al guardar precios');
      toast.success('Precios actualizados correctamente');
      setEditingPrice(null);
      loadAdminData();
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Error al guardar precios');
    } finally {
      setSavingPrices(false);
    }
  }

  if (loading && !adminStats) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Panel de Administracion</h2>
        <p className="text-muted-foreground">Gestion del sistema ContaEC</p>
      </div>

      <Tabs value={activeAdminTab} onValueChange={setActiveAdminTab} className="space-y-4">
        <TabsList className="flex flex-wrap h-auto gap-1">
          <TabsTrigger value="overview" className="gap-1.5">
            <Activity className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">Resumen</span>
          </TabsTrigger>
          <TabsTrigger value="users" className="gap-1.5">
            <Users className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">Usuarios</span>
          </TabsTrigger>
          <TabsTrigger value="system" className="gap-1.5">
            <Server className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">Sistema</span>
          </TabsTrigger>
          <TabsTrigger value="licenses" className="gap-1.5">
            <Key className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">Licencias</span>
          </TabsTrigger>
          <TabsTrigger value="security" className="gap-1.5">
            <ShieldAlert className="h-3.5 w-3.5" />
            <span className="hidden sm:inline">Seguridad</span>
          </TabsTrigger>
        </TabsList>

        {/* Overview Tab */}
        <TabsContent value="overview">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card>
              <CardContent className="p-6 text-center">
                <Users className="h-8 w-8 mx-auto text-primary mb-2" />
                <div className="text-3xl font-bold">{adminStats?.total_users ?? 0}</div>
                <p className="text-sm text-muted-foreground">Total Usuarios</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6 text-center">
                <Building2 className="h-8 w-8 mx-auto text-primary mb-2" />
                <div className="text-3xl font-bold">{adminStats?.total_companies ?? 0}</div>
                <p className="text-sm text-muted-foreground">Total Empresas</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6 text-center">
                <Database className="h-8 w-8 mx-auto text-primary mb-2" />
                <div className="text-3xl font-bold">{adminStats?.total_clients ?? 0}</div>
                <p className="text-sm text-muted-foreground">Total Clientes</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6 text-center">
                <Clock className="h-8 w-8 mx-auto text-amber-500 mb-2" />
                <div className="text-3xl font-bold">{adminStats?.expiring_licenses ?? 0}</div>
                <p className="text-sm text-muted-foreground">Licencias por Expirar (30d)</p>
              </CardContent>
            </Card>
            <Card>
              <CardContent className="p-6 text-center">
                <XCircle className="h-8 w-8 mx-auto text-destructive mb-2" />
                <div className="text-3xl font-bold">{adminStats?.expired_licenses ?? 0}</div>
                <p className="text-sm text-muted-foreground">Licencias Expiradas</p>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Users Tab */}
        <TabsContent value="users">
          <Card>
            <CardHeader>
              <CardTitle>Usuarios del Sistema</CardTitle>
              <CardDescription>Gestione usuarios y licencias</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Nombre</TableHead>
                      <TableHead>Email</TableHead>
                      <TableHead>Licencia</TableHead>
                      <TableHead>Expiracion</TableHead>
                      <TableHead>Estado</TableHead>
                      <TableHead>Acciones</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    {adminUsers.map((u) => (
                      <TableRow key={u.id}>
                        <TableCell className="font-medium">{u.full_name}</TableCell>
                        <TableCell>{u.email}</TableCell>
                        <TableCell>
                          <Badge variant="outline" className="capitalize">{u.license_type || 'N/A'}</Badge>
                        </TableCell>
                        <TableCell>
                          {u.license_end_date
                            ? new Date(u.license_end_date).toLocaleDateString('es-EC')
                            : 'Sin limite'}
                        </TableCell>
                        <TableCell>
                          <Badge variant={u.is_active ? 'default' : 'destructive'}>
                            {u.is_active ? 'Activo' : 'Inactivo'}
                          </Badge>
                        </TableCell>
                        <TableCell>
                          <div className="flex gap-2">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => { setSelectedUserId(u.id); setLicenseDialogOpen(true); setLicenseForm({ license_type: u.license_type }); }}
                            >
                              Licencia
                            </Button>
                            <Button
                              size="sm"
                              variant={u.is_active ? 'destructive' : 'default'}
                              onClick={() => handleToggleUser(u.id, u.is_active)}
                            >
                              {u.is_active ? 'Desactivar' : 'Activar'}
                            </Button>
                          </div>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* System Tab */}
        <TabsContent value="system">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">
                  <Server className="h-4 w-4 text-primary" />
                  Aplicacion
                </CardTitle>
              </CardHeader>
              <CardContent>
                {health ? (
                  <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Version</span>
                      <Badge variant="outline" className="font-mono">{(health.application as Record<string, string>)?.version ?? 'N/A'}</Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Ambiente</span>
                      <Badge variant={(health.application as Record<string, string>)?.environment === 'production' ? 'destructive' : 'default'}>
                        {(health.application as Record<string, string>)?.environment ?? 'N/A'}
                      </Badge>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Uptime</span>
                      <span className="text-sm font-medium">{(health.application as Record<string, string>)?.uptime ?? 'N/A'}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">Python</span>
                      <span className="text-sm font-mono">{(health.application as Record<string, string>)?.python_version ?? ''}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-muted-foreground">SO</span>
                      <span className="text-sm font-medium">{(health.application as Record<string, string>)?.system ?? ''}</span>
                    </div>
                    <Separator />
                    <div className="text-xs text-muted-foreground">
                      <p>Para cambiar ambiente, edite <code className="bg-muted px-1">APP_ENV</code> en <code className="bg-muted px-1">.env</code> y reinicie el servidor.</p>
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground text-center py-4">Cargando...</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Recursos del Sistema</CardTitle>
              </CardHeader>
              <CardContent>
                {health ? (
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">CPU</span>
                        <span className="font-medium">
                          {typeof (health.system as Record<string, unknown>)?.cpu_percent === 'number'
                            ? `${(health.system as Record<string, number>)?.cpu_percent}%`
                            : String((health.system as Record<string, unknown>)?.cpu_percent ?? 'N/A')}
                        </span>
                      </div>
                      {typeof (health.system as Record<string, unknown>)?.cpu_percent === 'number' && (
                        <div className="h-2 bg-muted rounded-full overflow-hidden mt-1">
                          <div className="h-full bg-primary transition-all" style={{ width: `${(health.system as Record<string, number>)?.cpu_percent}%` }} />
                        </div>
                      )}
                    </div>
                    <div>
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Memoria</span>
                        <span className="font-medium">
                          {typeof (health.system as Record<string, unknown>)?.memory_percent === 'number'
                            ? `${(health.system as Record<string, number>)?.memory_percent}%`
                            : String((health.system as Record<string, unknown>)?.memory_percent ?? 'N/A')}
                        </span>
                      </div>
                      {typeof (health.system as Record<string, unknown>)?.memory_percent === 'number' && (
                        <>
                          <div className="h-2 bg-muted rounded-full overflow-hidden mt-1">
                            <div className="h-full bg-primary transition-all" style={{ width: `${(health.system as Record<string, number>)?.memory_percent}%` }} />
                          </div>
                          <p className="text-xs text-muted-foreground mt-1">
                            {((health.system as Record<string, number>)?.memory_used_mb ?? 0).toFixed(0)} MB / {((health.system as Record<string, number>)?.memory_total_mb ?? 0).toFixed(0)} MB
                          </p>
                        </>
                      )}
                    </div>
                    <div>
                      <div className="flex justify-between text-sm">
                        <span className="text-muted-foreground">Disco</span>
                        <span className="font-medium">
                          {typeof (health.system as Record<string, unknown>)?.disk_percent === 'number'
                            ? `${(health.system as Record<string, number>)?.disk_percent}%`
                            : String((health.system as Record<string, unknown>)?.disk_percent ?? 'N/A')}
                        </span>
                      </div>
                      {typeof (health.system as Record<string, unknown>)?.disk_percent === 'number' && (
                        <>
                          <div className="h-2 bg-muted rounded-full overflow-hidden mt-1">
                            <div className={`h-full transition-all ${(health.system as Record<string, number>)?.disk_percent > 90 ? 'bg-destructive' : 'bg-primary'}`} style={{ width: `${(health.system as Record<string, number>)?.disk_percent}%` }} />
                          </div>
                          <p className="text-xs text-muted-foreground mt-1">
                            {((health.system as Record<string, number>)?.disk_used_gb ?? 0).toFixed(1)} GB / {((health.system as Record<string, number>)?.disk_total_gb ?? 0).toFixed(1)} GB
                          </p>
                        </>
                      )}
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground text-center py-4">Cargando...</p>
                )}
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="text-base">Base de Datos</CardTitle>
              </CardHeader>
              <CardContent>
                {health ? (
                  <div className="space-y-3">
                    <div className="flex justify-between p-3 rounded-lg border">
                      <span className="text-sm">Usuarios</span>
                      <span className="font-medium">{(health.database as Record<string, number>)?.total_users ?? 'N/A'}</span>
                    </div>
                    <div className="flex justify-between p-3 rounded-lg border">
                      <span className="text-sm">Empresas</span>
                      <span className="font-medium">{(health.database as Record<string, number>)?.total_companies ?? 'N/A'}</span>
                    </div>
                    <div className="flex justify-between p-3 rounded-lg border">
                      <span className="text-sm">Clientes</span>
                      <span className="font-medium">{(health.database as Record<string, number>)?.total_clients ?? 'N/A'}</span>
                    </div>
                  </div>
                ) : (
                  <p className="text-sm text-muted-foreground text-center py-4">Cargando...</p>
                )}
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        {/* Licenses Tab */}
        <TabsContent value="licenses">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-medium">Precios de Licencias</h3>
            <div className="flex gap-2">
              {editingPrice ? (
                <>
                  <Button variant="outline" size="sm" onClick={() => { setEditingPrice(null); loadAdminData(); }}>
                    Cancelar
                  </Button>
                  <Button size="sm" onClick={handleSavePrices} disabled={savingPrices}>
                    {savingPrices ? <Loader2 className="h-4 w-4 animate-spin mr-1" /> : null}
                    Guardar Precios
                  </Button>
                </>
              ) : (
                <Button variant="outline" size="sm" onClick={() => setEditingPrice('prices')}>
                  <Pencil className="h-3.5 w-3.5 mr-1" />
                  Editar Precios
                </Button>
              )}
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {licensePrices.map((plan) => (
              <Card key={plan.key} className="border-2">
                <CardHeader className="pb-3">
                  <CardTitle className="text-lg">{plan.type}</CardTitle>
                  <CardDescription>{plan.months} {plan.months === 1 ? 'mes' : 'meses'}</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center">
                    {editingPrice ? (
                      <div className="flex items-center justify-center gap-1">
                        <span className="text-lg font-bold">$</span>
                        <Input
                          type="number"
                          step="0.01"
                          min="0"
                          className="w-24 text-center text-xl font-bold"
                          value={priceForm[plan.key] ?? plan.price}
                          onChange={(e) => setPriceForm({ ...priceForm, [plan.key]: parseFloat(e.target.value) || 0 })}
                        />
                      </div>
                    ) : (
                      <span className="text-3xl font-bold">${plan.price.toFixed(2)}</span>
                    )}
                    <p className="text-xs text-muted-foreground mt-1">
                      ${((priceForm[plan.key] ?? plan.price) / plan.months).toFixed(2)}/mes
                    </p>
                  </div>
                  <Badge className={`w-full justify-center mt-3 ${plan.color}`}>{plan.type}</Badge>
                </CardContent>
              </Card>
            ))}
          </div>
          <Card className="mt-6">
            <CardHeader>
              <CardTitle className="text-base">Limites por Plan</CardTitle>
              <CardDescription>Caracteristicas y limites de cada tipo de licencia</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="overflow-x-auto">
                <Table>
                  <TableHeader>
                    <TableRow>
                      <TableHead>Limite</TableHead>
                      <TableHead>Mensual</TableHead>
                      <TableHead>Trimestral</TableHead>
                      <TableHead>Semestral</TableHead>
                      <TableHead>Anual</TableHead>
                    </TableRow>
                  </TableHeader>
                  <TableBody>
                    <TableRow><TableCell className="font-medium">Empresas max.</TableCell><TableCell>1</TableCell><TableCell>2</TableCell><TableCell>5</TableCell><TableCell>Ilimitado</TableCell></TableRow>
                    <TableRow><TableCell className="font-medium">Usuarios/empresa</TableCell><TableCell>2</TableCell><TableCell>5</TableCell><TableCell>10</TableCell><TableCell>Ilimitado</TableCell></TableRow>
                    <TableRow><TableCell className="font-medium">Comprobantes/mes</TableCell><TableCell>50</TableCell><TableCell>200</TableCell><TableCell>500</TableCell><TableCell>Ilimitado</TableCell></TableRow>
                    <TableRow><TableCell className="font-medium">Empleados</TableCell><TableCell>5</TableCell><TableCell>15</TableCell><TableCell>50</TableCell><TableCell>Ilimitado</TableCell></TableRow>
                    <TableRow><TableCell className="font-medium">Productos</TableCell><TableCell>100</TableCell><TableCell>500</TableCell><TableCell>2,000</TableCell><TableCell>Ilimitado</TableCell></TableRow>
                  </TableBody>
                </Table>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Security Tab */}
        <TabsContent value="security">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <ShieldAlert className="h-5 w-5 text-amber-500" />
                Problemas de Seguridad
              </CardTitle>
              <CardDescription>Usuarios con licencias expiradas pero activos, y sin configuracion</CardDescription>
            </CardHeader>
            <CardContent>
              {securityData ? (
                <div className="space-y-6">
                  <div>
                    <h3 className="text-sm font-medium mb-3 flex items-center gap-2">
                      <XCircle className="h-4 w-4 text-destructive" />
                      Licencias Expiradas pero Activas ({securityData.expired_active_licenses.length})
                    </h3>
                    {securityData.expired_active_licenses.length > 0 ? (
                      <Table>
                        <TableHeader>
                          <TableRow><TableHead>Usuario</TableHead><TableHead>Email</TableHead><TableHead>Expiro</TableHead><TableHead>Dias</TableHead></TableRow>
                        </TableHeader>
                        <TableBody>
                          {securityData.expired_active_licenses.map((u) => (
                            <TableRow key={u.user_id}>
                              <TableCell className="font-medium">{u.full_name}</TableCell>
                              <TableCell>{u.email}</TableCell>
                              <TableCell>{u.license_end_date ? new Date(u.license_end_date).toLocaleDateString('es-EC') : 'N/A'}</TableCell>
                              <TableCell className="text-destructive">{u.days_expired ?? 'N/A'}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    ) : (
                      <p className="text-sm text-muted-foreground">No hay problemas</p>
                    )}
                  </div>
                  <Separator />
                  <div>
                    <h3 className="text-sm font-medium mb-3 flex items-center gap-2">
                      <AlertTriangle className="h-4 w-4 text-amber-500" />
                      Usuarios sin Configuracion ({securityData.users_without_config.length})
                    </h3>
                    {securityData.users_without_config.length > 0 ? (
                      <Table>
                        <TableHeader>
                          <TableRow><TableHead>Usuario</TableHead><TableHead>Email</TableHead></TableRow>
                        </TableHeader>
                        <TableBody>
                          {securityData.users_without_config.map((u) => (
                            <TableRow key={u.user_id}>
                              <TableCell className="font-medium">{u.full_name}</TableCell>
                              <TableCell>{u.email}</TableCell>
                            </TableRow>
                          ))}
                        </TableBody>
                      </Table>
                    ) : (
                      <p className="text-sm text-muted-foreground">Todos los usuarios tienen configuracion</p>
                    )}
                  </div>
                </div>
              ) : (
                <p className="text-sm text-muted-foreground text-center py-4">Cargando...</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>

      {/* License Dialog */}
      <Dialog open={licenseDialogOpen} onOpenChange={setLicenseDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Modificar Licencia</DialogTitle>
            <DialogDescription>Seleccione el tipo de licencia para el usuario</DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label>Tipo de Licencia</Label>
              <select
                className="w-full rounded-md border px-3 py-2 text-sm"
                value={licenseForm.license_type}
                onChange={(e) => setLicenseForm({ license_type: e.target.value })}
              >
                {licensePrices.map((p) => (
                  <option key={p.key} value={p.key}>{p.type} - ${p.price.toFixed(2)}</option>
                ))}
              </select>
            </div>
            <Button onClick={handleModifyLicense} disabled={modifying} className="w-full">
              {modifying ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : null}
              Guardar Cambios
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  );
}
