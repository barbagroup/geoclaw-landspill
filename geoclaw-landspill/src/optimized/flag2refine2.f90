! ::::::::::::::::::::: flag2refine ::::::::::::::::::::::::::::::::::
!
! User routine to control flagging of points for refinement.
!
! Specific for landspill applications. It flags a cell for refinement only when
!   1. it is a wet cell
!   2. the cell center is inside a must-refined region
!
! ::::::::::::::::::::: flag2refine ::::::::::::::::::::::::::::::::::
subroutine flag2refine2(&
    mx, my, mbc, mbuff, meqn, maux, xlower, ylower, dx, dy, t, level, &
    tolsp, q, aux, amrflags)

    use amr_module, only: mxnest, t0, DOFLAG, UNSET
    use topo_module, only: tlowtopo, thitopo, xlowtopo, xhitopo, ylowtopo, yhitopo
    use topo_module, only: minleveltopo, mtopofiles
    use landspill_module, only: point_sources, refine_tol
    implicit none

    ! Subroutine arguments
    integer, intent(in) :: mx, my, mbc, meqn, maux, level, mbuff
    real(kind=8), intent(in) :: xlower, ylower, dx, dy, t, tolsp
    real(kind=8), intent(in) :: q(meqn, 1-mbc:mx+mbc, 1-mbc:my+mbc)
    real(kind=8), intent(in) :: aux(maux, 1-mbc:mx+mbc, 1-mbc:my+mbc)
    real(kind=8), intent(in out) :: amrflags(1-mbuff:mx+mbuff, 1-mbuff:my+mbuff)

    ! external functions
    logical, external :: allowflag

    ! Generic local variables
    integer :: i, j, m
    real(kind=8) :: xc, yc

    ! if t == t0, flag the cells containing point sources
    if (t .eq. t0) then ! should we use abs(...) .lt. some tolerance?
        call point_sources%flag_cells(mbuff, mx, my, xlower, ylower, dx, dy, amrflags)
    endif

    ! Loop over interior points on this grid
    ! (i, j) cell: centered at (xc, yc)
    y_loop: do j = 1, my
        yc = ylower + (j - 0.5d0) * dy

        x_loop: do i = 1, mx
            xc = xlower + (i - 0.5d0) * dx

            ! skip because this cell has been flagged to flag or don't flat
            if (amrflags(i,j) .ne. UNSET) cycle x_loop

            ! Check to see if refinement is forced in any topography file region
            do m = 1, mtopofiles
                if (level < minleveltopo(m) .and. t >= tlowtopo(m) .and. t <= thitopo(m)) then
                    if (xc .ge. xlowtopo(m) .and. xc .le. xhitopo(m) .and. yc .ge. ylowtopo(m) .and. yc .le. yhitopo(m)) then
                        amrflags(i,j) = DOFLAG
                        cycle x_loop
                    endif
                endif
            enddo

            ! flag whenever this is a wet cell
            if (allowflag(xc, yc, t, level) .and. (q(1, i, j) > refine_tol)) amrflags(i, j) = DOFLAG

        enddo x_loop
    enddo y_loop
end subroutine flag2refine2
