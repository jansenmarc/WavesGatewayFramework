import {
  AfterViewInit,
  Attribute,
  ChangeDetectorRef,
  Directive,
  HostBinding,
  Input,
  OnInit
} from '@angular/core';
import { PublicConfigurationService } from './public.configuration.service';

@Directive({
  selector: 'button[appPrimary]'
})
export class PrimaryButtonDirective implements AfterViewInit {
  private primaryColor: string;

  @HostBinding('style.background-color') backgroundColor: string;
  @HostBinding('style.border-color') borderColor: string;
  @HostBinding('style.color') color: string;

  @Input('invert') invert: string | undefined;

  constructor(
    configService: PublicConfigurationService,
    private cd: ChangeDetectorRef
  ) {
    this.primaryColor = configService.configuration.web_primary_color;
  }

  ngAfterViewInit(): void {
    if (this.invert !== undefined) {
      this.backgroundColor = 'white';
      this.color = this.primaryColor;
      this.borderColor = this.primaryColor;
    } else {
      this.backgroundColor = this.primaryColor;
      this.borderColor = this.primaryColor;
    }

    this.cd.detectChanges();
  }
}
