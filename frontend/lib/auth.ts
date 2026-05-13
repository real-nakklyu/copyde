import { getSupabaseClient } from "@/lib/supabaseClient"

export async function signIn(email: string, password: string) {
  return getSupabaseClient().auth.signInWithPassword({ email, password })
}

export async function signUp(email: string, password: string, displayName: string) {
  return getSupabaseClient().auth.signUp({ email, password, options: { data: { display_name: displayName } } })
}

export async function signOut() {
  return getSupabaseClient().auth.signOut()
}

